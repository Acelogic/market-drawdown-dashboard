# S&P 500 Intra-Year Drawdowns Generator

## Quick Prompt

```
Fetch the latest data from https://www.slickcharts.com/sp500/drawdown and update the sp500_drawdowns.html file with all intra-year drawdowns sorted from largest to smallest. Then export it as a long PNG image.
```

## Full Prompt (if starting fresh)

```
Fetch ALL intra-year drawdown data from https://www.slickcharts.com/sp500/drawdown - get every single year from 1928 to present. Create an HTML page that:
- Sorts all years by drawdown percentage (biggest to smallest)
- Shows rank, year, and drawdown with visual bars
- Color codes by severity (red >20%, orange 10-20%, green <10%)
- Dark theme with good contrast

Save it to this folder as sp500_drawdowns.html, then export as a long PNG image.
```

## Manual Export Commands

Sorted table (long image):
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --screenshot=sp500_drawdowns.png --window-size=1200,4800 "file:///Users/mcruz/Developer/sp500-drawdowns/sp500_drawdowns.html"
```

Decades summary (worst/avg/median):
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --screenshot=sp500_decades_avg.png --window-size=1050,1400 "file:///Users/mcruz/Developer/sp500-drawdowns/sp500_decades_avg.html"
```

## Data Source

https://www.slickcharts.com/sp500/drawdown

## Files

- `sp500_drawdowns.html` - Sorted table of all years
- `sp500_drawdowns.png` - Sorted table image
- `sp500_decades_avg.html` - Decades summary (worst year, avg, median)
- `sp500_decades_avg.png` - Decades summary image
- `PROMPT.md` - This file
