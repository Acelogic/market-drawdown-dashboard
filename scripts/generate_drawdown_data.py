#!/usr/bin/env python3
"""
Generate intra-year drawdown data for S&P 500, Nasdaq 100, and Nasdaq Composite.

Downloads daily prices from Yahoo Finance and calculates drawdowns using the
SlickCharts methodology: decline from previous year's closing price to the
year's intra-day low. Writes JSON files to data/.

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

# Fallback previous-year closes for years before Yahoo Finance data begins.
# Source: SlickCharts S&P 500 drawdown table.
PREV_YEAR_CLOSE_FALLBACKS = {
    "^GSPC": {1928: 17.66},  # 1927 close
}

DATA_DIR = Path(__file__).parent.parent / "data"


def calculate_yearly_stats(close_prices, low_prices, symbol):
    """
    Given pandas Series of daily closing and intra-day low prices indexed by date,
    return a list of {"year": int, "drawdown": float, "return": float} dicts.

    drawdown: decline from previous year's last close to the year's intra-day low (%).
              Matches SlickCharts methodology. Capped at 0 if the low never undercuts
              the previous year's close.
    return: full-year return from previous year's last close to this year's last close (%)
    """
    results = []
    grouped_close = close_prices.groupby(close_prices.index.year)
    grouped_low = low_prices.groupby(low_prices.index.year)
    fallbacks = PREV_YEAR_CLOSE_FALLBACKS.get(symbol, {})
    prev_year_last_close = None

    for year, close_group in sorted(grouped_close):
        if len(close_group) < 2:
            prev_year_last_close = float(close_group.values[-1])
            continue

        # Use hardcoded fallback if no previous year data exists
        if prev_year_last_close is None and year in fallbacks:
            prev_year_last_close = fallbacks[year]

        low_group = grouped_low.get_group(year)
        year_low = float(low_group.min())

        # Year return: use previous year's last close as start if available
        start_price = prev_year_last_close if prev_year_last_close else float(close_group.values[0])
        end_price = float(close_group.values[-1])
        year_return = ((end_price - start_price) / start_price) * 100

        # Drawdown: decline from prev year close to year's intra-day low
        if prev_year_last_close and year_low < prev_year_last_close:
            drawdown = ((year_low - prev_year_last_close) / prev_year_last_close) * 100
        else:
            drawdown = 0.0

        results.append({
            "year": int(year),
            "drawdown": round(drawdown, 2),
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
        low = hist["Low"]
        print(f"  Got {len(close)} daily prices from {close.index[0].date()} to {close.index[-1].date()}")

        yearly_stats = calculate_yearly_stats(close, low, symbol)
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
