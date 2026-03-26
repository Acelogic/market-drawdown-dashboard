# Market Drawdown Dashboard — Design Spec

## Overview

A live drawdown dashboard showing the current drawdown from all-time high for three indices: S&P 500, Nasdaq 100 (NDX), and Nasdaq Composite. Styled after SlickCharts (light cream background, clean financial aesthetic). Deployed on GitHub Pages.

## Indices

| Index | Symbol | Historical Data From | Source |
|-------|--------|---------------------|--------|
| S&P 500 | `^GSPC` | 1928 | SlickCharts (existing hardcoded data) |
| Nasdaq 100 | `^NDX` | 1985 | Self-calculated from Yahoo Finance daily prices |
| Nasdaq Composite | `^IXIC` | 1971 | Self-calculated from Yahoo Finance daily prices |

## Architecture

### Single HTML file (`index.html`)

No build tools, no framework. One self-contained HTML file with inline CSS and JS.

- **CSS**: Inline `<style>` block. SlickCharts-inspired: light cream `#FBFCEA` background, white cards with subtle shadows, Arial/Helvetica, clean spacing.
- **JS**: Inline `<script>` block. Fetches live quotes on page load and every 60 seconds during market hours.
- **Historical data**: Hardcoded JSON arrays embedded in the JS for all three indices' intra-year drawdowns.

### Data pipeline (one-time Python script)

A Python script `scripts/generate_drawdown_data.py` that:

1. Downloads daily closing prices from Yahoo Finance (`yfinance` library) for `^NDX` (1985-present) and `^IXIC` (1971-present)
2. For each calendar year, calculates the maximum intra-year drawdown:
   - Track the running peak (highest close seen so far that year)
   - For each day, compute `(close - peak) / peak`
   - The year's intra-year drawdown is the minimum of these values
3. Outputs JSON to `data/ndx_drawdowns.json` and `data/ixic_drawdowns.json`
4. This data gets copy-pasted or auto-injected into `index.html`

S&P 500 historical data is already available from the existing project and SlickCharts.

The script can be re-run anytime to refresh historical data (e.g., at year-end to add the completed year).

### Live data (client-side)

On page load and every 60 seconds:

1. Fetch current quotes for `^GSPC`, `^NDX`, `^IXIC` from Yahoo Finance's public chart API endpoint
2. Compare current price to known all-time high (hardcoded, updated periodically)
3. Calculate current drawdown: `(current - ATH) / ATH`
4. Update the three drawdown cards
5. For the current year's row in the table, update with the live intra-year drawdown (tracking the running YTD peak)

**API endpoint**: Yahoo Finance chart API (`query1.finance.yahoo.com/v8/finance/chart/`). This is a public endpoint used by Yahoo's own frontend. For CORS from GitHub Pages, we'll proxy through `corsproxy.io` (e.g., `https://corsproxy.io/?https://query1.finance.yahoo.com/v8/finance/chart/^GSPC`). If `corsproxy.io` is down, the page falls back gracefully.

**Fallback**: If the API call fails (rate limit, CORS block), the page still renders with historical data and shows "Live data unavailable" on the cards.

## Page Layout

### 1. Header
- Title: "Market Drawdown Dashboard"
- Subtitle: "Live intraday data • Last updated: [timestamp] • Auto-refreshes every 60s"
- Centered, clean typography

### 2. Three Drawdown Cards (side-by-side)
Each card shows:
- Index name (uppercase label)
- Current drawdown % (large, bold, red)
- All-time high price
- Current price
- Date of ATH

### 3. Intra-Year Drawdown Comparison Table
- Sorted by worst drawdown across all three indices (the worst single-index drawdown in any given year determines the row's rank)
- Columns: Rank, Year, S&P 500 bar + %, NDX bar + %, Composite bar + %
- Color-coded bars: S&P 500 = red `#e74c3c`, NDX = blue `#3498db`, Composite = purple `#9b59b6`
- Years before an index existed show a `—` dash
- Current year row highlighted to distinguish live data from historical
- Legend above the table

### 4. Footer
- Data source attribution (Yahoo Finance for live, SlickCharts for S&P 500 historical)
- Index inception dates

## Visual Design

- **Background**: Light cream `#FBFCEA`
- **Cards**: White `#fff`, `border-radius: 8px`, `box-shadow: 0 0 10px rgba(0,0,0,0.08)`
- **Font**: Arial, Helvetica, sans-serif
- **Max-width**: 1200px centered container
- **Responsive**: Cards stack vertically on mobile (< 768px), table scrolls horizontally
- **Severity coloring on drawdown %**: > 20% bold red, 10-20% orange, < 10% green (applied to the percentage text, not the bars — bars keep their index color)

## Deployment

- GitHub Pages from the `main` branch
- Repository: evolve the existing `sp500-drawdowns` repo or create a new one (user's choice)
- Just push `index.html` and any static assets

## File Structure

```
sp500-drawdowns/
├── index.html                  # The dashboard (new)
├── scripts/
│   └── generate_drawdown_data.py  # One-time data generation script
├── data/
│   ├── ndx_drawdowns.json      # Generated NDX historical data
│   └── ixic_drawdowns.json     # Generated Composite historical data
├── sp500_drawdowns.html        # Existing project (keep as-is)
├── sp500_decades_avg.html      # Existing project (keep as-is)
├── PROMPT.md                   # Existing project notes
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-03-26-drawdown-dashboard-design.md  # This spec
```

## Sorting Logic

The table is sorted by the worst single-index drawdown in each year. For example, if in 2002 S&P 500 had -33.1% and NDX had -47.8%, the row ranks by -47.8%. This ensures the most dramatic market events float to the top regardless of which index was hit hardest.

## Scope Exclusions

- No backend server
- No user authentication
- No database
- No charting library (bars are pure CSS divs, like the existing project)
- No historical daily price chart (just the ranked drawdown table)
- No build tools or bundler
