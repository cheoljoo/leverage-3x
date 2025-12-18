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
  - Includes: Dot-com Bubble, 9/11, Financial Crisis, COVID-19, SVB Collapse, and more

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

## License

MIT

## Author

Cheol Joo (cheoljoo@gmail.com)
