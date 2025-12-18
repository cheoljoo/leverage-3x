# Leveraged Investment Analysis Tool

A Python tool for analyzing daily 10,000 KRW investments in 3x and 4x leveraged S&P 500 (SPY) and Nasdaq 100 (QQQ) products, for strategic investment decisions.

## Introduction

This project is inspired by [this YouTube video](https://youtube.com/shorts/TlbQ3ao86Cg?si=bP0XwIYXbGonwUnu), which demonstrates the power of 3x-leveraged investment strategies.

## Inspiration

- The Nasdaq is closing in on the S&P 500, so I think it's a great time to buy.
- Usually, we'll just buy stocks on a regular basis. But when the Nasdaq and S&P 500 charts look like they're closing in on each other, I think buying more will really pay off.

## Features

- **Daily Investment Simulation**: Models daily 10,000 KRW purchases from any date range
- **Multiple Leverage Options**: Analyze both 3x and 4x leveraged strategies
- **Flexible Date Range**: Specify custom start/end dates with `--start` and `--end`
- **Display Control**: Use `--size` parameter to show only the last N years while maintaining full calculations
- **Multi-chart Visualization**: 
  - 3x Leverage chart
  - 4x Leverage chart
  - 3x vs 4x Comparison
  - Price comparison with dual Y-axes
  - Difference analysis (Nasdaq - S&P500 cumulative value)
  - Daily return rate visualization
  - Return rate difference analysis (Nasdaq Return - S&P500 Return)
- **Automatic Date Adjustment**: Automatically detects and adjusts to earliest available QQQ data (1999-03-10)
- **Financial Events Markers**: Marks major financial events (2000-2024) on all graphs with vertical lines and labels
  - Dynamically loaded from `events.json` file
  - Includes: Dot-com Bubble, 9/11, Financial Crisis, COVID-19, SVB Collapse, FOMC rate changes, and more
  - 31 curated financial events (0-3 per year)

## Requirements

- Python 3.13+
- Dependencies: `yfinance`, `pandas`, `matplotlib`

## Installation

```bash
# Clone the repository
git clone https://github.com/cheoljoo/leverage-3x.git
cd leverage-3x

# Install with uv (recommended)
uv sync
```

## Usage

### Basic Usage (Default: 2016-01-01 to Today)
```bash
uv run main.py
```

### With Custom Date Range
```bash
uv run main.py --start 2020-01-01 --end 2024-12-31
```

### With Display Size (Show last 3 years, but calculate from start date)
```bash
uv run main.py --start 2020-01-01 --end 2024-12-31 --size 3
```

### Options
- `--start YYYY-MM-DD`: Start date for calculation (default: 2016-01-01)
- `--end YYYY-MM-DD`: End date for calculation (default: today)
- `--size N`: Display only the last N years in graphs, while maintaining full calculations (default: 0, shows all)

## Output

The tool generates 7 high-resolution PNG charts:
1. `leverage_3x_investment_[dates].png` - 3x leverage analysis with cumulative investment value
2. `leverage_4x_investment_[dates].png` - 4x leverage analysis with cumulative investment value
3. `leverage_comparison_[dates].png` - Direct comparison of 3x vs 4x leverage strategies
4. `leverage_with_prices_[dates].png` - Investment value with raw stock prices overlay (dual Y-axes)
5. `leverage_difference_[dates].png` - Difference visualization showing Nasdaq(3x/4x) - S&P500(3x/4x)
6. `leverage_return_rate_[dates].png` - Daily return rate (%) for 3x and 4x strategies
7. `leverage_return_rate_diff_[dates].png` - Return rate difference showing Nasdaq Return - S&P500 Return for 3x and 4x

## Example Output

```
============================================================
Leveraged Investment Analysis
============================================================
Period: 2023-01-01 to 2024-12-31

3x Leverage Final Values:
  S&P 500 (SPY): ₩6,289,054
  Nasdaq 100 (QQQ): ₩6,621,938

4x Leverage Final Values:
  S&P 500 (SPY): ₩6,289,054
  Nasdaq 100 (QQQ): ₩6,621,938

```

## How It Works

### Daily Investment Simulation
- Each day, 10,000 KRW is invested in the stock
- Number of shares = 10,000 KRW / (Stock Price × 1,200)
- Portfolio value accumulates over time

### Leverage Calculation
- Daily returns are multiplied by the leverage factor (3x or 4x)
- Compound returns are calculated: `(1 + leveraged_return).cumprod() - 1`

### Daily Return Rate Calculation
- Formula: `(Investment Value - Principal) / Principal × 100 (%)`
- Principal = 10,000 KRW × number of days invested
- Shows profitability percentage at each point in time

### Difference Analysis
- Compares cumulative investment values between Nasdaq and S&P 500
- Separate 3x and 4x leverage difference visualization
- Helps identify which index is outperforming
- Color-coded: green for positive difference (Nasdaq ahead), red for negative (S&P 500 ahead)

### Automatic Date Adjustment
- When requesting data before QQQ availability (before 1999-03-10), automatically adjusts to earliest available date
- Prevents errors and ensures all analyses are valid

### Financial Events Markers
- Marks major financial events on all charts from 2000 onwards
- Events include:
  - **2000-03-10**: Dot-com Bubble peak
  - **2001-09-11**: 9/11 Terrorist attacks
  - **2008-09-15**: Lehman Brothers collapse
  - **2009-03-09**: Financial crisis market bottom
  - **2011-08-05**: US credit downgrade
  - **2020-03-23**: COVID-19 market crash
  - **2021-01-28**: GME short squeeze event
  - **2022-09-28**: UK gilt crisis
  - **2023-03-10**: Silicon Valley Bank collapse
  - **2024-08-05**: Japan yen crisis
- Helps understand how major events correlate with investment performance

## Customizing Financial Events

### Overview

Financial events are stored in an external `events.json` file, making it easy to add, remove, or modify events without editing Python code. The tool loads events dynamically from this JSON file at runtime.

### Adding or Editing Financial Events

#### Step 1: Open the events.json file
```bash
vi /home/cheoljoo/code/leverage-3x/events.json
# Or use your preferred editor (VSCode, nano, etc.)
```

#### Step 2: Event JSON Format

Each event in `events.json` follows this structure:
```json
{
  "date": "YYYY-MM-DD",
  "label": "Event Name or Rate Change",
  "description": "Event Description"
}
```

#### Step 3: Add Your Event

Add a new object to the JSON array:
```json
[
  {
    "date": "2000-03-10",
    "label": "Dot-com Bubble Peak",
    "description": "Tech bubble peak"
  },
  ...existing events...,
  {
    "date": "2025-01-15",
    "label": "My Custom Event",
    "description": "Add your event description here"
  }
]
```

#### Event Format Details

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| **date** | `YYYY-MM-DD` | `2025-01-15` | Must be within your data range (typically 1999-present) |
| **label** | String | `Fed Rate Hike 0.75%` | Appears as label on graph (keep reasonably short) |
| **description** | String | `Interest rate increase` | Additional context for the event |

#### FOMC Rate Change Format

For Federal Reserve rate decisions, use this label format to show rate transitions:
```json
{
  "date": "2022-07-27",
  "label": "1.50-1.75% -> 2.25-2.50% (Final: 2.50%)",
  "description": "Fed Rate Hike 2022 (0.75% increase)"
}
```

Format: `previous_range -> new_range (Final: new_rate%)`

#### Important Notes

1. **Valid JSON**: Ensure the JSON is properly formatted (matching braces, commas, quotes)
2. **Date Format**: Always use `YYYY-MM-DD` format
3. **Chronological Order**: While not required, keep events in date order for readability
4. **Data Range**: Events are only displayed if:
   - The date falls within your `--start` and `--end` parameters
   - The date exists in the actual data
5. **Last Comma**: Don't add a trailing comma after the last object in the array

#### Step 4: Save and Run

```bash
cd /home/cheoljoo/code/leverage-3x
uv run main.py --start 2020-01-01 --end 2024-12-31
```

Your new events will automatically appear on all 7 graphs as vertical lines with labels at the top!

### Current Financial Events (31 Events)

The tool comes with 31 pre-configured financial events, including:

#### Major Crisis Events
- **2001-09-11**: 9/11 Terrorist Attacks
- **2008-09-15**: Lehman Brothers Collapse
- **2009-03-09**: Financial Crisis Market Low
- **2020-02-20**: COVID-19 Market Crash Begins

#### Significant FOMC Rate Changes (≥0.50%)
- **2020-03-15**: Fed Emergency Cuts (1.00% reduction) - COVID-19 response
- **2022-07-27**: Fed Rate Hike (0.75% increase) - Inflation fighting

#### Market Events & Crises
- **2010-05-06**: Flash Crash
- **2011-08-05**: US Credit Downgrade
- **2021-01-28**: GME Short Squeeze
- **2021-03-26**: Archegos Collapse
- **2021-11-15**: Inflation Concerns
- **2022-02-24**: Russia-Ukraine War
- **2022-09-28**: UK Gilt Crisis
- **2023-03-10**: SVB Collapse
- **2023-03-19**: Credit Suisse Rescue
- **2024-08-05**: Japan Yen Crisis

#### Tariff & Trade Events
- **2018-03-08**: Trump Tariffs (Steel & Aluminum)
- **2019-05-10**: US-China Tariff Escalation

#### And More...

See `events.json` for the complete list of all 31 events.

## License
## License

MIT

## Author

Cheol Joo (cheoljoo@gmail.com)
