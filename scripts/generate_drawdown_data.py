#!/usr/bin/env python3
"""
Generate intra-year drawdown data for S&P 500, Nasdaq 100, and Nasdaq Composite.

Downloads daily closing prices from Yahoo Finance, calculates the maximum
intra-year drawdown for each calendar year, and writes JSON files to data/.

Usage:
    python scripts/generate_drawdown_data.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

import yfinance as yf

INDICES = {
    "sp500": {"symbol": "^GSPC", "start": "1928-01-01", "name": "S&P 500"},
    "ndx": {"symbol": "^NDX", "start": "1985-01-01", "name": "Nasdaq 100"},
    "ixic": {"symbol": "^IXIC", "start": "1971-01-01", "name": "Nasdaq Composite"},
}

DATA_DIR = Path(__file__).parent.parent / "data"


def calculate_yearly_stats(daily_prices):
    """
    Given a pandas Series of daily closing prices indexed by date,
    return a list of {"year": int, "drawdown": float, "return": float} dicts.

    drawdown: worst peak-to-trough decline within each calendar year (negative %)
    return: full-year return from first close to last close (%)
    """
    results = []
    grouped = daily_prices.groupby(daily_prices.index.year)
    prev_year_last_close = None

    for year, group in sorted(grouped):
        if len(group) < 2:
            prev_year_last_close = float(group.values[-1])
            continue
        prices = group.values

        # Max intra-year drawdown
        peak = prices[0]
        max_drawdown = 0.0
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (price - peak) / peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown

        # Year return: use previous year's last close as start if available
        start_price = prev_year_last_close if prev_year_last_close else float(prices[0])
        end_price = float(prices[-1])
        year_return = ((end_price - start_price) / start_price) * 100

        results.append({
            "year": int(year),
            "drawdown": round(max_drawdown * 100, 2),
            "return": round(year_return, 2),
        })
        prev_year_last_close = end_price

    return results


def find_all_time_high(daily_prices):
    """
    Return the all-time high price and the date it occurred.
    """
    ath_idx = daily_prices.idxmax()
    return {
        "price": round(float(daily_prices[ath_idx]), 2),
        "date": ath_idx.strftime("%Y-%m-%d"),
    }


def main():
    DATA_DIR.mkdir(exist_ok=True)

    for key, config in INDICES.items():
        symbol = config["symbol"]
        start = config["start"]
        name = config["name"]

        print(f"Downloading {name} ({symbol}) from {start}...")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start, end=datetime.now().strftime("%Y-%m-%d"))

        if hist.empty:
            print(f"  WARNING: No data returned for {symbol}. Skipping.")
            continue

        close = hist["Close"]
        print(f"  Got {len(close)} daily prices from {close.index[0].date()} to {close.index[-1].date()}")

        yearly_stats = calculate_yearly_stats(close)
        ath = find_all_time_high(close)

        output = {
            "index": name,
            "symbol": symbol,
            "ath": ath,
            "drawdowns": yearly_stats,
        }

        out_path = DATA_DIR / f"{key}_drawdowns.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"  Wrote {len(yearly_stats)} years to {out_path}")

    print("\nDone. Files written to data/")


if __name__ == "__main__":
    main()
