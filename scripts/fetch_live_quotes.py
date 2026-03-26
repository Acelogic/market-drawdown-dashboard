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
        + "?range=1d&interval=5m"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    meta = data["chart"]["result"][0]["meta"]
    return {
        "price": meta["regularMarketPrice"],
        "previousClose": meta.get("chartPreviousClose", meta.get("previousClose")),
        "marketState": meta.get("marketState", "UNKNOWN"),
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
