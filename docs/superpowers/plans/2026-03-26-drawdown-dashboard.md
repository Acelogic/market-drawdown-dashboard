# Market Drawdown Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a live drawdown dashboard for S&P 500, Nasdaq 100, and Nasdaq Composite with historical intra-year drawdown comparison table, deployed on GitHub Pages.

**Architecture:** Single `index.html` with inline CSS/JS. A Python script generates historical NDX and Composite drawdown data from Yahoo Finance daily prices. The HTML page embeds all historical data and fetches live quotes via Yahoo Finance API (through corsproxy.io for CORS) to show current drawdowns.

**Tech Stack:** Python 3 + yfinance (data generation), vanilla HTML/CSS/JS (dashboard), GitHub Pages (deployment)

---

## File Structure

| File | Purpose |
|------|---------|
| `scripts/generate_drawdown_data.py` | Downloads daily prices from Yahoo Finance, calculates intra-year drawdowns for all 3 indices, outputs JSON |
| `data/sp500_drawdowns.json` | Generated S&P 500 intra-year drawdowns (1928-present) |
| `data/ndx_drawdowns.json` | Generated Nasdaq 100 intra-year drawdowns (1985-present) |
| `data/ixic_drawdowns.json` | Generated Nasdaq Composite intra-year drawdowns (1971-present) |
| `index.html` | The dashboard — CSS, JS, and hardcoded historical data all inline |

---

### Task 1: Initialize Git Repo

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize the repository**

```bash
cd /Users/mcruz/Developer/sp500-drawdowns
git init
```

- [ ] **Step 2: Create .gitignore**

```gitignore
__pycache__/
*.pyc
.superpowers/
.DS_Store
*.png
```

- [ ] **Step 3: Commit existing files and gitignore**

```bash
git add .gitignore PROMPT.md sp500_drawdowns.html sp500_decades_avg.html docs/
git commit -m "init: existing S&P 500 drawdown project + dashboard design spec"
```

---

### Task 2: Write the Data Generation Script

**Files:**
- Create: `scripts/generate_drawdown_data.py`
- Create: `data/` (directory)

This script downloads daily closing prices from Yahoo Finance and calculates intra-year drawdowns for all three indices. It also extracts the current all-time high price and date for each index, which the dashboard needs for the live drawdown cards.

- [ ] **Step 1: Install yfinance**

```bash
pip install yfinance
```

Expected: Successfully installed yfinance and dependencies.

- [ ] **Step 2: Create the script**

Create `scripts/generate_drawdown_data.py`:

```python
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


def calculate_intra_year_drawdowns(daily_prices):
    """
    Given a pandas Series of daily closing prices indexed by date,
    return a list of {"year": int, "drawdown": float} dicts.

    Drawdown is the worst peak-to-trough decline within each calendar year,
    expressed as a negative percentage (e.g., -32.16 for -32.16%).
    """
    results = []
    grouped = daily_prices.groupby(daily_prices.index.year)

    for year, group in grouped:
        if len(group) < 2:
            continue
        prices = group.values
        peak = prices[0]
        max_drawdown = 0.0
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (price - peak) / peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown
        results.append({"year": int(year), "drawdown": round(max_drawdown * 100, 2)})

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

        drawdowns = calculate_intra_year_drawdowns(close)
        ath = find_all_time_high(close)

        output = {
            "index": name,
            "symbol": symbol,
            "ath": ath,
            "drawdowns": drawdowns,
        }

        out_path = DATA_DIR / f"{key}_drawdowns.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"  Wrote {len(drawdowns)} years to {out_path}")

    print("\nDone. Files written to data/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the script**

```bash
cd /Users/mcruz/Developer/sp500-drawdowns
python scripts/generate_drawdown_data.py
```

Expected output:
```
Downloading S&P 500 (^GSPC) from 1928-01-01...
  Got XXXXX daily prices from YYYY-MM-DD to YYYY-MM-DD
  Wrote XX years to data/sp500_drawdowns.json
Downloading Nasdaq 100 (^NDX) from 1985-01-01...
  Got XXXXX daily prices from YYYY-MM-DD to YYYY-MM-DD
  Wrote XX years to data/ndx_drawdowns.json
Downloading Nasdaq Composite (^IXIC) from 1971-01-01...
  Got XXXXX daily prices from YYYY-MM-DD to YYYY-MM-DD
  Wrote XX years to data/ixic_drawdowns.json

Done. Files written to data/
```

- [ ] **Step 4: Verify the output**

```bash
cat data/sp500_drawdowns.json | python -m json.tool | head -30
cat data/ndx_drawdowns.json | python -m json.tool | head -30
cat data/ixic_drawdowns.json | python -m json.tool | head -30
```

Check that:
- Each file has an `ath` object with `price` and `date`
- Each file has a `drawdowns` array with `year` and `drawdown` entries
- S&P 500 starts around 1928, NDX around 1985, Composite around 1971
- Known values roughly match: S&P 2008 should be around -49%, 2020 around -32%

Note: Yahoo Finance may not have S&P 500 data back to 1928. If it only goes back to ~1950, that's fine — we'll supplement with the existing hardcoded data from the SlickCharts project for earlier years. Check the earliest year in `sp500_drawdowns.json` and note any gap.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_drawdown_data.py data/
git commit -m "feat: add drawdown data generation script with output for all 3 indices"
```

---

### Task 3: Build the Dashboard HTML — Structure and CSS

**Files:**
- Create: `index.html`

This task creates the full HTML file with all CSS and the static page structure (header, cards, table shell, footer). No JS yet — just the visual layout with placeholder values.

- [ ] **Step 1: Create index.html with full CSS and HTML structure**

Create `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Drawdown Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #FBFCEA;
            min-height: 100vh;
            padding: 30px 20px;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 24px;
        }
        .header h1 {
            font-size: 1.75em;
            color: #222;
            margin-bottom: 6px;
        }
        .header .subtitle {
            font-size: 0.85rem;
            color: #888;
        }
        .header .status {
            font-size: 0.8rem;
            color: #aaa;
            margin-top: 4px;
        }
        .status .live-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #40C28A;
            border-radius: 50%;
            margin-right: 4px;
            animation: pulse 2s infinite;
        }
        .status .error-dot {
            background: #e74c3c;
            animation: none;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* Drawdown Cards */
        .cards {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }
        .card {
            flex: 1;
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.08);
            text-align: center;
        }
        .card .label {
            font-size: 0.7rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .card .drawdown-value {
            font-size: 2.2rem;
            font-weight: bold;
            margin: 4px 0;
        }
        .card .detail {
            font-size: 0.75rem;
            color: #666;
            line-height: 1.6;
        }
        .card .ath-date {
            font-size: 0.7rem;
            color: #aaa;
            margin-top: 4px;
        }

        /* Severity colors for drawdown values */
        .severity-severe { color: #e74c3c; }
        .severity-high { color: #e67e22; }
        .severity-moderate { color: #f39c12; }
        .severity-mild { color: #27ae60; }

        /* Table */
        .table-section {
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.08);
        }
        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        .table-header h2 {
            font-size: 1rem;
            color: #222;
        }
        .legend {
            display: flex;
            gap: 16px;
            font-size: 0.75rem;
            color: #666;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .legend-swatch {
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }
        .swatch-sp500 { background: #e74c3c; }
        .swatch-ndx { background: #3498db; }
        .swatch-ixic { background: #9b59b6; }

        table {
            width: 100%;
            border-collapse: collapse;
        }
        thead th {
            padding: 10px 8px;
            text-align: left;
            font-size: 0.7rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #eee;
        }
        thead th:first-child { width: 40px; text-align: center; }
        thead th:nth-child(2) { width: 55px; }
        tbody tr {
            border-bottom: 1px solid #f5f5f5;
        }
        tbody tr:hover {
            background: #fafaf0;
        }
        tbody tr.current-year {
            background: #fffff0;
            border-left: 3px solid #f39c12;
        }
        tbody td {
            padding: 6px 8px;
            font-size: 0.8rem;
            vertical-align: middle;
        }
        tbody td:first-child {
            text-align: center;
            color: #bbb;
            font-size: 0.75rem;
        }
        .year-cell {
            font-weight: 600;
            color: #333;
        }
        .bar-cell {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .bar-track {
            flex: 1;
            height: 14px;
            background: #f0f0e8;
            border-radius: 2px;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            border-radius: 2px;
            min-width: 1px;
        }
        .bar-fill-sp500 { background: #e74c3c; opacity: 0.85; }
        .bar-fill-ndx { background: #3498db; opacity: 0.85; }
        .bar-fill-ixic { background: #9b59b6; opacity: 0.85; }
        .pct-label {
            min-width: 50px;
            text-align: right;
            font-weight: 600;
            font-size: 0.75rem;
        }
        .pct-sp500 { color: #e74c3c; }
        .pct-ndx { color: #3498db; }
        .pct-ixic { color: #9b59b6; }
        .na-label {
            color: #ddd;
            text-align: center;
            font-size: 0.75rem;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.75rem;
            color: #999;
            line-height: 1.6;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .cards { flex-direction: column; }
            .table-section { overflow-x: auto; }
            table { min-width: 700px; }
            .legend { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Market Drawdown Dashboard</h1>
            <div class="subtitle">S&P 500 &bull; Nasdaq 100 &bull; Nasdaq Composite</div>
            <div class="status" id="status">
                <span class="live-dot" id="status-dot"></span>
                <span id="status-text">Loading live data...</span>
            </div>
        </div>

        <!-- Drawdown Cards -->
        <div class="cards">
            <div class="card" id="card-sp500">
                <div class="label">S&P 500</div>
                <div class="drawdown-value" id="dd-sp500">&mdash;</div>
                <div class="detail" id="detail-sp500">Loading...</div>
                <div class="ath-date" id="ath-date-sp500"></div>
            </div>
            <div class="card" id="card-ndx">
                <div class="label">Nasdaq 100</div>
                <div class="drawdown-value" id="dd-ndx">&mdash;</div>
                <div class="detail" id="detail-ndx">Loading...</div>
                <div class="ath-date" id="ath-date-ndx"></div>
            </div>
            <div class="card" id="card-ixic">
                <div class="label">Nasdaq Composite</div>
                <div class="drawdown-value" id="dd-ixic">&mdash;</div>
                <div class="detail" id="detail-ixic">Loading...</div>
                <div class="ath-date" id="ath-date-ixic"></div>
            </div>
        </div>

        <!-- Comparison Table -->
        <div class="table-section">
            <div class="table-header">
                <h2>Intra-Year Drawdowns</h2>
                <div class="legend">
                    <div class="legend-item"><div class="legend-swatch swatch-sp500"></div>S&P 500</div>
                    <div class="legend-item"><div class="legend-swatch swatch-ndx"></div>Nasdaq 100</div>
                    <div class="legend-item"><div class="legend-swatch swatch-ixic"></div>Nasdaq Composite</div>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Year</th>
                        <th>S&P 500</th>
                        <th></th>
                        <th>Nasdaq 100</th>
                        <th></th>
                        <th>Composite</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    <!-- Populated by JS -->
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div class="footer">
            Data: Yahoo Finance (live), SlickCharts (S&P 500 pre-1950 historical)<br>
            S&P 500 from 1928 &bull; Nasdaq Composite from 1971 &bull; Nasdaq 100 from 1985
        </div>
    </div>

    <script>
    // JS will be added in Task 4
    </script>
</body>
</html>
```

- [ ] **Step 2: Open in browser and verify layout**

```bash
open /Users/mcruz/Developer/sp500-drawdowns/index.html
```

Verify: cream background, three white cards with placeholder values, empty table, footer text, responsive on resize.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add dashboard HTML structure and CSS (no JS yet)"
```

---

### Task 4: Add Historical Data and Table Rendering JS

**Files:**
- Modify: `index.html` (replace the `<script>` block)

This task embeds the generated historical drawdown data as JS objects and writes the code that renders the comparison table. No live data yet — just the static historical table.

**Note on DOM construction:** The table is built using DOM APIs (`document.createElement`, `textContent`) rather than string concatenation to avoid any XSS surface area, even though the data is all hardcoded numeric values we control.

- [ ] **Step 1: Read the generated JSON files**

```bash
cat /Users/mcruz/Developer/sp500-drawdowns/data/sp500_drawdowns.json
cat /Users/mcruz/Developer/sp500-drawdowns/data/ndx_drawdowns.json
cat /Users/mcruz/Developer/sp500-drawdowns/data/ixic_drawdowns.json
```

You need the `drawdowns` arrays from each file. Also note the `ath` object from each.

- [ ] **Step 2: Replace the `<script>` block in index.html**

Replace the placeholder `<script>// JS will be added in Task 4</script>` with the full script block. The data arrays below are placeholders — **replace them with the actual data from the JSON files generated in Task 2**.

```javascript
// ===== HISTORICAL DATA =====
// Paste the drawdowns arrays from the generated JSON files.
// Format: { year: number, drawdown: number } where drawdown is negative percentage
// Example: { year: 2008, drawdown: -49.53 }

const SP500_DATA = [/* PASTE sp500_drawdowns.json .drawdowns array here */];
const NDX_DATA = [/* PASTE ndx_drawdowns.json .drawdowns array here */];
const IXIC_DATA = [/* PASTE ixic_drawdowns.json .drawdowns array here */];

// All-time highs from generated data (used by live data in Task 5)
const ATH = {
    sp500: { price: 0, date: "" }, // PASTE from sp500_drawdowns.json .ath
    ndx: { price: 0, date: "" },   // PASTE from ndx_drawdowns.json .ath
    ixic: { price: 0, date: "" },  // PASTE from ixic_drawdowns.json .ath
};

// ===== TABLE RENDERING =====

function getSeverityClass(pct) {
    const abs = Math.abs(pct);
    if (abs >= 20) return "severity-severe";
    if (abs >= 14) return "severity-high";
    if (abs >= 10) return "severity-moderate";
    return "severity-mild";
}

function buildTableData() {
    // Collect all unique years
    const yearSet = new Set();
    SP500_DATA.forEach(d => yearSet.add(d.year));
    NDX_DATA.forEach(d => yearSet.add(d.year));
    IXIC_DATA.forEach(d => yearSet.add(d.year));

    // Index data by year for quick lookup
    const sp500Map = Object.fromEntries(SP500_DATA.map(d => [d.year, d.drawdown]));
    const ndxMap = Object.fromEntries(NDX_DATA.map(d => [d.year, d.drawdown]));
    const ixicMap = Object.fromEntries(IXIC_DATA.map(d => [d.year, d.drawdown]));

    // Build rows with worst drawdown for sorting
    const rows = [];
    for (const year of yearSet) {
        const sp = sp500Map[year] ?? null;
        const ndx = ndxMap[year] ?? null;
        const ixic = ixicMap[year] ?? null;
        const worst = Math.min(
            sp ?? 0,
            ndx ?? 0,
            ixic ?? 0
        );
        rows.push({ year, sp500: sp, ndx, ixic, worst });
    }

    // Sort by worst drawdown (most negative first)
    rows.sort((a, b) => a.worst - b.worst);
    return rows;
}

function createBarCell(drawdown, fillClass, pctClass) {
    // Returns a document fragment with one or two <td> elements
    const frag = document.createDocumentFragment();
    if (drawdown === null) {
        const td = document.createElement("td");
        td.colSpan = 2;
        const div = document.createElement("div");
        div.className = "na-label";
        div.textContent = "\u2014"; // em dash
        td.appendChild(div);
        frag.appendChild(td);
        return frag;
    }
    const maxDrawdown = 50; // scale bars relative to -50%
    const width = Math.min(Math.abs(drawdown) / maxDrawdown * 100, 100);

    // Bar cell
    const tdBar = document.createElement("td");
    const barCell = document.createElement("div");
    barCell.className = "bar-cell";
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = "bar-fill " + fillClass;
    fill.style.width = width + "%";
    track.appendChild(fill);
    barCell.appendChild(track);
    tdBar.appendChild(barCell);
    frag.appendChild(tdBar);

    // Pct cell
    const tdPct = document.createElement("td");
    const span = document.createElement("span");
    span.className = "pct-label " + pctClass;
    span.textContent = drawdown.toFixed(1) + "%";
    tdPct.appendChild(span);
    frag.appendChild(tdPct);

    return frag;
}

function renderTable() {
    const rows = buildTableData();
    const currentYear = new Date().getFullYear();
    const tbody = document.getElementById("table-body");
    tbody.textContent = ""; // clear existing rows

    rows.forEach((row, i) => {
        const tr = document.createElement("tr");
        if (row.year === currentYear) {
            tr.className = "current-year";
        }

        // Rank
        const tdRank = document.createElement("td");
        tdRank.textContent = i + 1;
        tr.appendChild(tdRank);

        // Year
        const tdYear = document.createElement("td");
        tdYear.className = "year-cell";
        tdYear.textContent = row.year;
        tr.appendChild(tdYear);

        // S&P 500 bar + pct
        tr.appendChild(createBarCell(row.sp500, "bar-fill-sp500", "pct-sp500"));

        // NDX bar + pct
        tr.appendChild(createBarCell(row.ndx, "bar-fill-ndx", "pct-ndx"));

        // Composite bar + pct
        tr.appendChild(createBarCell(row.ixic, "bar-fill-ixic", "pct-ixic"));

        tbody.appendChild(tr);
    });
}

// Initial render
renderTable();
```

- [ ] **Step 3: Open in browser and verify the table**

```bash
open /Users/mcruz/Developer/sp500-drawdowns/index.html
```

Verify:
- Table is populated with all years, sorted worst-first
- S&P 500 shows data from ~1928 (or whenever Yahoo data starts)
- NDX shows data from ~1985, em dash for earlier years
- Composite shows data from ~1971, em dash for earlier years
- Color-coded bars and percentage labels render correctly
- Current year row has yellow highlight with left border

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add historical drawdown data and table rendering"
```

---

### Task 5: Add Live Data Fetching

**Files:**
- Modify: `index.html` (add live data code at the end of the `<script>` block)

This task adds the Yahoo Finance API fetch, updates the drawdown cards with live data, and updates the current year's table row.

- [ ] **Step 1: Add live data fetching code**

Append this to the end of the `<script>` block in `index.html`, after the `renderTable()` call:

```javascript
// ===== LIVE DATA =====

const SYMBOLS = {
    sp500: "^GSPC",
    ndx: "^NDX",
    ixic: "^IXIC",
};

const LABELS = {
    sp500: "S&P 500",
    ndx: "Nasdaq 100",
    ixic: "Nasdaq Composite",
};

// YTD peaks — initialized from ATH but updated with live data
const ytdPeaks = {
    sp500: ATH.sp500.price,
    ndx: ATH.ndx.price,
    ixic: ATH.ixic.price,
};

async function fetchQuote(symbol) {
    const url = "https://corsproxy.io/?" + encodeURIComponent(
        "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol + "?range=1d&interval=1m"
    );
    const resp = await fetch(url);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const data = await resp.json();
    const meta = data.chart.result[0].meta;
    return {
        price: meta.regularMarketPrice,
        previousClose: meta.previousClose,
        marketState: meta.marketState, // "REGULAR", "PRE", "POST", "CLOSED"
    };
}

function formatPrice(price) {
    return price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function updateCard(key, quote) {
    const ath = ATH[key];
    const currentPrice = quote.price;

    // Update YTD peak if current price exceeds it (new ATH)
    if (currentPrice > ytdPeaks[key]) {
        ytdPeaks[key] = currentPrice;
    }
    if (currentPrice > ath.price) {
        ath.price = currentPrice;
        ath.date = new Date().toISOString().split("T")[0];
    }

    const drawdownFromATH = ((currentPrice - ath.price) / ath.price) * 100;

    const ddEl = document.getElementById("dd-" + key);
    const detailEl = document.getElementById("detail-" + key);
    const athDateEl = document.getElementById("ath-date-" + key);

    ddEl.textContent = drawdownFromATH.toFixed(2) + "%";
    ddEl.className = "drawdown-value " + getSeverityClass(drawdownFromATH);

    detailEl.textContent = "ATH: " + formatPrice(ath.price) + " \u2022 Now: " + formatPrice(currentPrice);
    athDateEl.textContent = "ATH date: " + ath.date;
}

function updateCurrentYearRow(key, quote) {
    const currentYear = new Date().getFullYear();
    const currentPrice = quote.price;

    // Calculate YTD drawdown from YTD peak
    const ytdDrawdown = ((currentPrice - ytdPeaks[key]) / ytdPeaks[key]) * 100;

    // Update the table data and re-render
    const dataMap = { sp500: SP500_DATA, ndx: NDX_DATA, ixic: IXIC_DATA };
    const arr = dataMap[key];
    const entry = arr.find(d => d.year === currentYear);
    if (entry) {
        entry.drawdown = Math.min(entry.drawdown, Math.round(ytdDrawdown * 100) / 100);
    }
}

async function refreshLiveData() {
    const statusDot = document.getElementById("status-dot");
    const statusText = document.getElementById("status-text");

    try {
        const results = await Promise.all([
            fetchQuote(SYMBOLS.sp500),
            fetchQuote(SYMBOLS.ndx),
            fetchQuote(SYMBOLS.ixic),
        ]);

        const keys = ["sp500", "ndx", "ixic"];
        keys.forEach(function(key, i) {
            updateCard(key, results[i]);
            updateCurrentYearRow(key, results[i]);
        });

        // Re-render table with updated current year data
        renderTable();

        var now = new Date();
        var timeStr = now.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", second: "2-digit" });
        var marketState = results[0].marketState;
        var stateLabel = marketState === "REGULAR" ? "Market Open" :
                         marketState === "PRE" ? "Pre-Market" :
                         marketState === "POST" ? "After Hours" : "Market Closed";

        statusDot.className = "live-dot";
        statusText.textContent = stateLabel + " \u2022 Last updated: " + timeStr + " \u2022 Auto-refreshes every 60s";
    } catch (err) {
        console.error("Failed to fetch live data:", err);
        statusDot.className = "live-dot error-dot";
        statusText.textContent = "Live data unavailable \u2022 Showing historical data only";
    }
}

// Fetch immediately, then every 60 seconds
refreshLiveData();
setInterval(refreshLiveData, 60000);
```

- [ ] **Step 2: Open in browser and verify live data**

```bash
open /Users/mcruz/Developer/sp500-drawdowns/index.html
```

Verify:
- Three cards update with current drawdown percentages, prices, and ATH dates
- Status bar shows market state and last updated time
- Green pulsing dot while live data is working
- If API fails (e.g., CORS issue), red dot and fallback message appear, table still renders with historical data
- Current year row in the table updates with live YTD drawdown
- Console has no errors (check DevTools)

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add live data fetching from Yahoo Finance with auto-refresh"
```

---

### Task 6: Supplement Pre-1950 S&P 500 Data

**Files:**
- Modify: `index.html` (may need to add hardcoded entries for early years)

Yahoo Finance's S&P 500 data typically starts around 1950. The existing `sp500_drawdowns.html` has data from 1928. This task fills the gap.

- [ ] **Step 1: Check what years are missing**

Look at `data/sp500_drawdowns.json` — note the earliest year. Compare against the existing data in `sp500_drawdowns.html` which has entries from 1928-1949.

- [ ] **Step 2: Add missing years to the SP500_DATA array**

Extract the pre-1950 data from the existing `sp500_drawdowns.html` file (years 1928-1949 with their drawdown percentages). Add these entries to the beginning of the `SP500_DATA` array in `index.html`.

The existing data from `sp500_drawdowns.html` for these years:

```javascript
// Pre-1950 data from SlickCharts (Yahoo Finance doesn't go back this far)
{year: 1928, drawdown: -4.02},
{year: 1929, drawdown: -27.47},
{year: 1930, drawdown: -32.68},
{year: 1931, drawdown: -49.67},
{year: 1932, drawdown: -45.81},
{year: 1933, drawdown: -20.09},
{year: 1934, drawdown: -16.15},
{year: 1935, drawdown: -15.16},
{year: 1936, drawdown: -0.22},
{year: 1937, drawdown: -40.80},
{year: 1938, drawdown: -19.43},
{year: 1939, drawdown: -20.70},
{year: 1940, drawdown: -27.85},
{year: 1941, drawdown: -20.89},
{year: 1942, drawdown: -14.04},
{year: 1943, drawdown: 0.00},
{year: 1944, drawdown: -0.94},
{year: 1945, drawdown: -0.53},
{year: 1946, drawdown: -18.66},
{year: 1947, drawdown: -10.00},
{year: 1948, drawdown: -9.54},
{year: 1949, drawdown: -10.86},
```

Merge these with the Yahoo Finance data, avoiding duplicates (if Yahoo starts at 1950, just prepend; if there's overlap, keep the SlickCharts values for pre-1950 and Yahoo values for 1950+).

- [ ] **Step 3: Verify in browser**

Confirm the table now shows entries going back to 1928 for S&P 500 and the data looks correct. 1931 should be #1 or #2 worst with -49.67%.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add pre-1950 S&P 500 drawdown data from SlickCharts"
```

---

### Task 7: Deploy to GitHub Pages

**Files:**
- No new files

- [ ] **Step 1: Create the GitHub repository**

```bash
cd /Users/mcruz/Developer/sp500-drawdowns
gh repo create sp500-drawdowns --public --source=. --push
```

If the repo already exists, just add the remote and push:
```bash
git remote add origin https://github.com/mcruz/sp500-drawdowns.git
git push -u origin main
```

- [ ] **Step 2: Enable GitHub Pages**

```bash
gh api repos/{owner}/{repo}/pages -X POST -f source.branch=main -f source.path=/
```

Or via the GitHub UI: Settings > Pages > Source: Deploy from branch > main > / (root).

- [ ] **Step 3: Verify the deployment**

Wait 1-2 minutes, then visit the GitHub Pages URL (typically `https://<username>.github.io/sp500-drawdowns/`).

Verify:
- Page loads with the cream background and three cards
- Live data fetches successfully (check that corsproxy.io works from the deployed domain)
- Historical table renders correctly
- Responsive on mobile

- [ ] **Step 4: Commit any fixes if needed**

If CORS or other deployment issues arise, fix and push.

---

### Task 8: Final Polish and README

**Files:**
- Modify: `PROMPT.md` (update with new project info)

- [ ] **Step 1: Update PROMPT.md**

Update `PROMPT.md` to document the new dashboard alongside the existing project files. Add instructions for:
- How to regenerate historical data: `python scripts/generate_drawdown_data.py`
- How to update the ATH values after a new all-time high
- The GitHub Pages URL
- Data sources and limitations

- [ ] **Step 2: Final browser check**

Open `index.html` locally and verify:
- All three cards show live drawdowns
- Table is complete with all years, sorted correctly
- Pre-index years show em dash
- Current year is highlighted
- Mobile responsive
- No console errors

- [ ] **Step 3: Commit and push**

```bash
git add PROMPT.md
git commit -m "docs: update PROMPT.md with dashboard instructions"
git push
```
