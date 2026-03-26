# Market Drawdown Dashboard

**Live:** http://mcruz.me/market-drawdown-dashboard/

## What It Does

Live drawdown dashboard showing the current drawdown from all-time high for S&P 500, Nasdaq 100, and Nasdaq Composite. Includes a historical intra-year drawdown comparison table going back to 1928.

- Fetches live intraday prices from Yahoo Finance (via corsproxy.io)
- Auto-refreshes every 60 seconds during market hours
- Falls back gracefully to historical data if the API is unavailable

## Regenerating Historical Data

```bash
python scripts/generate_drawdown_data.py
```

Downloads daily prices from Yahoo Finance, calculates intra-year drawdowns for all three indices, and writes JSON to `data/`. After running, paste the updated data arrays into `index.html`.

## Data Sources

- **Live prices:** Yahoo Finance chart API (via corsproxy.io CORS proxy)
- **Historical S&P 500:** Yahoo Finance daily prices (1928-present)
- **Historical Nasdaq 100:** Yahoo Finance daily prices (1985-present)
- **Historical Nasdaq Composite:** Yahoo Finance daily prices (1971-present)

## Files

- `index.html` - The live dashboard (deployed to GitHub Pages)
- `scripts/generate_drawdown_data.py` - Historical data generation script
- `data/sp500_drawdowns.json` - Generated S&P 500 drawdown data
- `data/ndx_drawdowns.json` - Generated Nasdaq 100 drawdown data
- `data/ixic_drawdowns.json` - Generated Nasdaq Composite drawdown data

### Legacy Files (original S&P-only project)

- `sp500_drawdowns.html` - Static sorted table (dark theme)
- `sp500_decades_avg.html` - Decades summary
- `PROMPT.md` - This file

## Manual Export Commands (legacy)

Sorted table:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --screenshot=sp500_drawdowns.png --window-size=1200,4800 "file:///Users/mcruz/Developer/sp500-drawdowns/sp500_drawdowns.html"
```

Decades summary:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --screenshot=sp500_decades_avg.png --window-size=1050,1400 "file:///Users/mcruz/Developer/sp500-drawdowns/sp500_decades_avg.html"
```
