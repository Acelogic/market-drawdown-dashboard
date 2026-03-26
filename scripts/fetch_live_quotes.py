#!/usr/bin/env python3
"""
Fetch live quotes for SPY, QQQ, and ^IXIC from Yahoo Finance.
Writes data/live.json with current prices and market state.
Runs server-side (GitHub Action) so no CORS issues.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SYMBOLS = {
    "sp500": "^GSPC",
    "ndx": "^NDX",
    "ixic": "^IXIC",
}

DATA_DIR = Path(__file__).parent.parent / "data"


def fetch_quote(symbol):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + urllib.request.quote(symbol, safe="")
        + "?range=ytd&interval=1d"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    result = data["chart"]["result"][0]
    meta = result["meta"]

    price = meta["regularMarketPrice"]
    ath = meta["fiftyTwoWeekHigh"]
    low_since_ath = meta["fiftyTwoWeekLow"]

    # Find YTD low from actual price data if available
    closes = result.get("indicators", {}).get("quote", [{}])[0].get("low", [])
    valid_closes = [c for c in closes if c is not None]
    ytd_low = min(valid_closes) if valid_closes else low_since_ath

    drawdown_at_low = ((ytd_low - ath) / ath) * 100 if ath else 0
    drawdown_current = ((price - ath) / ath) * 100 if ath else 0
    gain_from_low = ((price - ytd_low) / ytd_low) * 100 if ytd_low else 0
    gain_to_ath = ((ath - price) / price) * 100 if price else 0

    return {
        "price": round(price, 2),
        "previousClose": meta.get("chartPreviousClose", meta.get("previousClose")),
        "marketState": meta.get("marketState", "UNKNOWN"),
        "fiftyTwoWeekHigh": round(ath, 2),
        "fiftyTwoWeekLow": round(low_since_ath, 2),
        "ytdLow": round(ytd_low, 2),
        "drawdownAtLow": round(drawdown_at_low, 2),
        "drawdownCurrent": round(drawdown_current, 2),
        "gainFromLow": round(gain_from_low, 2),
        "gainToATH": round(gain_to_ath, 2),
    }


def main():
    DATA_DIR.mkdir(exist_ok=True)
    results = {}
    for key, symbol in SYMBOLS.items():
        try:
            results[key] = fetch_quote(symbol)
            print(f"  {key}: ${results[key]['price']:.2f} ({results[key]['marketState']})")
        except Exception as e:
            print(f"  {key}: FAILED - {e}")

    if not results:
        print("All fetches failed, not writing live.json")
        return

    output = {
        "quotes": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    out_path = DATA_DIR / "live.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
