#!/usr/bin/env python3
"""
Leveraged Investment Analysis Tool

Simulates daily 10,000 KRW investments in 3x and 4x leveraged S&P 500 and Nasdaq 100 products
from 2016 to present day, with convergence signal detection.
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from datetime import datetime
import sys


def calculate_leveraged_investment(ticker, leverage_factor=3, start_date="2016-01-01", end_date=None):
    """
    Calculate the cumulative value of daily 10,000 KRW investments with leverage.
    
    Args:
        ticker: Stock ticker (e.g., 'SPY' for S&P 500, 'QQQ' for Nasdaq 100)
        leverage_factor: Leverage multiplier (default 3)
        start_date: Start date for analysis
        end_date: End date for analysis (default: today)
    
    Returns:
        DataFrame with calculated values
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Downloading {ticker} data from {start_date} to {end_date}...")
    
    # Download price data
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    # Handle MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        # Get the first level (price type)
        data.columns = data.columns.get_level_values(0)
    
    # Use 'Close' instead of 'Adj Close' (yfinance changed the default)
    close_col = 'Close' if 'Close' in data.columns else 'Adj Close'
    
    # Calculate daily returns
    data['Daily_Return'] = data[close_col].pct_change()
    
    # Apply leverage to returns
    data['Leveraged_Return'] = data['Daily_Return'] * leverage_factor
    
    # Calculate cumulative return (compound)
    data['Cumulative_Return'] = (1 + data['Leveraged_Return']).cumprod() - 1
    
    # Initialize investment tracking
    daily_investment = 10_000  # 10,000 KRW
    shares_held = []
    cumulative_value = []
    
    current_shares = 0
    
    for idx, row in data.iterrows():
        # Calculate price in KRW (assuming 1 USD = 1,200 KRW for simplicity)
        # In real scenario, use actual exchange rate
        price_krw = row[close_col] * 1200
        
        # Buy shares with daily investment
        if price_krw > 0:
            new_shares = daily_investment / price_krw
            current_shares += new_shares
        
        # Calculate current portfolio value
        current_value = current_shares * price_krw
        
        shares_held.append(current_shares)
        cumulative_value.append(current_value)
    
    data['Shares_Held'] = shares_held
    data['Cumulative_Value'] = cumulative_value
    
    return data


def detect_convergence_signals(sp500_data, nasdaq_data, window=15, threshold=50, min_gap=100):
    """
    Detect convergence signals when S&P 500 and Nasdaq 100 returns are similar.
    
    This identifies potential buying opportunities when both indices show similar performance.
    
    Args:
        sp500_data: S&P 500 investment DataFrame
        nasdaq_data: Nasdaq 100 investment DataFrame
        window: Rolling window size for smoothing (days)
        threshold: Threshold for convergence (return rate difference)
        min_gap: Minimum days between convergence signals
    
    Returns:
        convergence_signals: List of convergence signal dates
        rolling_diff: Series of rolling differences
    """
    # Calculate returns
    sp500_returns = (sp500_data['Cumulative_Value'] / sp500_data['Cumulative_Value'].iloc[0] - 1) * 100
    nasdaq_returns = (nasdaq_data['Cumulative_Value'] / nasdaq_data['Cumulative_Value'].iloc[0] - 1) * 100
    
    # Align indices
    min_len = min(len(sp500_returns), len(nasdaq_returns))
    sp500_returns = sp500_returns.iloc[:min_len]
    nasdaq_returns = nasdaq_returns.iloc[:min_len]
    
    # Calculate difference between returns
    return_diff = (sp500_returns - nasdaq_returns).abs()
    
    # Apply rolling average to smooth the difference
    rolling_diff = return_diff.rolling(window=window, center=True).mean()
    
    # Find convergence points (where difference is below threshold)
    convergence_mask = rolling_diff < threshold
    convergence_indices = convergence_mask[convergence_mask].index.tolist()
    
    if not convergence_indices:
        return [], rolling_diff
    
    # Group consecutive convergence dates and select the best one from each group
    convergence_signals = []
    current_group = [convergence_indices[0]]
    
    for i in range(1, len(convergence_indices)):
        if (convergence_indices[i] - current_group[-1]).days <= 1:
            current_group.append(convergence_indices[i])
        else:
            # End of current group, find the date with minimum difference
            best_date = min(current_group, key=lambda x: rolling_diff[x])
            convergence_signals.append(best_date)
            current_group = [convergence_indices[i]]
    
    # Don't forget the last group
    if current_group:
        best_date = min(current_group, key=lambda x: rolling_diff[x])
        convergence_signals.append(best_date)
    
    # Enforce minimum gap between signals
    filtered_signals = []
    for signal in convergence_signals:
        if not filtered_signals or (signal - filtered_signals[-1]).days >= min_gap:
            filtered_signals.append(signal)
    
    return filtered_signals, rolling_diff


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Leveraged Investment Analysis Tool')
    parser.add_argument('--start', type=str, default='2016-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default=None, help='End date (YYYY-MM-DD)')
    parser.add_argument('--size', type=int, default=0, help='Display size in years (0=all)')
    
    args = parser.parse_args()
    
    start_date = args.start
    end_date = args.end if args.end else datetime.now().strftime("%Y-%m-%d")
    display_size_years = args.size
    
    print("=" * 60)
    print("Leveraged Investment Analysis")
    print("=" * 60)
    
    # Adjust start_date if Nasdaq (QQQ) doesn't have data for that date
    # Nasdaq 100 index started in 1985, but QQQ ETF started in 1999
    print("Checking data availability for QQQ...")
    test_nasdaq = yf.download('QQQ', start=start_date, end=end_date, progress=False)
    
    # Handle MultiIndex columns
    if isinstance(test_nasdaq.columns, pd.MultiIndex):
        test_nasdaq.columns = test_nasdaq.columns.get_level_values(0)
    
    if len(test_nasdaq) == 0 or test_nasdaq.index[0] > pd.to_datetime(start_date):
        # QQQ doesn't have data for the requested start_date
        actual_start = test_nasdaq.index[0].strftime("%Y-%m-%d") if len(test_nasdaq) > 0 else None
        if actual_start:
            print(f"⚠ Nasdaq (QQQ) data not available from {start_date}")
            print(f"✓ Adjusting start date to {actual_start}")
            start_date = actual_start
        else:
            print(f"✗ Error: No Nasdaq (QQQ) data available for date range {start_date} to {end_date}")
            return
    
    print(f"Period: {start_date} to {end_date}\n")
    
    # Calculate 3x leverage
    print("Calculating 3x leverage...")
    sp500_3x = calculate_leveraged_investment('SPY', leverage_factor=3, 
                                             start_date=start_date, end_date=end_date)
    nasdaq_3x = calculate_leveraged_investment('QQQ', leverage_factor=3, 
                                              start_date=start_date, end_date=end_date)
    
    # Download raw price data for price comparison graphs
    print("Downloading raw price data...")
    sp500_prices = yf.download('SPY', start=start_date, end=end_date, progress=False)
    nasdaq_prices = yf.download('QQQ', start=start_date, end=end_date, progress=False)
    
    # Handle MultiIndex columns from yfinance
    if isinstance(sp500_prices.columns, pd.MultiIndex):
        sp500_prices.columns = sp500_prices.columns.get_level_values(0)
    if isinstance(nasdaq_prices.columns, pd.MultiIndex):
        nasdaq_prices.columns = nasdaq_prices.columns.get_level_values(0)
    
    # Determine which column to use (Close or Adj Close)
    sp500_close_col = 'Close' if 'Close' in sp500_prices.columns else 'Adj Close'
    nasdaq_close_col = 'Close' if 'Close' in nasdaq_prices.columns else 'Adj Close'
    
    # Calculate 4x leverage
    print("Calculating 4x leverage...")
    sp500_4x = calculate_leveraged_investment('SPY', leverage_factor=4, 
                                             start_date=start_date, end_date=end_date)
    nasdaq_4x = calculate_leveraged_investment('QQQ', leverage_factor=4, 
                                              start_date=start_date, end_date=end_date)
    
    # Calculate convergence signals
    convergence_signals_3x, rolling_diff_3x = detect_convergence_signals(sp500_3x, nasdaq_3x)
    convergence_signals_4x, rolling_diff_4x = detect_convergence_signals(sp500_4x, nasdaq_4x)
    
    # Calculate total investment
    total_investment = 10_000 / 1_000_000 * len(sp500_3x)  # in millions
    
    # Print results
    print(f"\n3x Leverage Final Values:")
    print(f"  S&P 500 (SPY): ₩{sp500_3x['Cumulative_Value'].iloc[-1]:,.0f}")
    print(f"  Nasdaq 100 (QQQ): ₩{nasdaq_3x['Cumulative_Value'].iloc[-1]:,.0f}")
    
    print(f"\n4x Leverage Final Values:")
    print(f"  S&P 500 (SPY): ₩{sp500_4x['Cumulative_Value'].iloc[-1]:,.0f}")
    print(f"  Nasdaq 100 (QQQ): ₩{nasdaq_4x['Cumulative_Value'].iloc[-1]:,.0f}")
    
    print(f"\n📊 Convergence Signals (Buy Opportunity Areas):")
    print(f"  3x Leverage: {len(convergence_signals_3x)} days detected")
    print(f"  4x Leverage: {len(convergence_signals_4x)} days detected")
    
    if len(convergence_signals_3x) > 0:
        convergence_dates_3x = [d.strftime('%Y-%m-%d') for d in convergence_signals_3x]
        print(f"  3x Convergence dates (first 10): {convergence_dates_3x[:10]}")
    
    # Calculate display date range based on --size parameter
    end_date_obj = pd.to_datetime(end_date)
    if display_size_years > 0:
        display_start_date = end_date_obj - pd.DateOffset(years=display_size_years)
        size_label = f" (Display Size: {display_size_years} year{'s' if display_size_years > 1 else ''})"
    else:
        display_start_date = pd.to_datetime(start_date)
        size_label = " (Display Size: All data)"
    
    # Create 3x Leverage visualization
    plt.figure(figsize=(14, 7))
    
    # Filter data by display date range (create mask for each dataset independently)
    mask_3x_sp500 = (sp500_3x.index >= display_start_date) & (sp500_3x.index <= end_date_obj)
    mask_3x_nasdaq = (nasdaq_3x.index >= display_start_date) & (nasdaq_3x.index <= end_date_obj)
    
    plt.plot(sp500_3x.index[mask_3x_sp500], sp500_3x.loc[mask_3x_sp500, 'Cumulative_Value'] / 1_000_000, 
             label='S&P 500 (3x Leverage)', linewidth=2, color='#1f77b4')
    plt.plot(nasdaq_3x.index[mask_3x_nasdaq], nasdaq_3x.loc[mask_3x_nasdaq, 'Cumulative_Value'] / 1_000_000, 
             label='Nasdaq 100 (3x Leverage)', linewidth=2, color='#ff7f0e')
    
    # Add convergence signal markers for 3x (filtered by display range)
    convergence_signals_3x_filtered = [d for d in convergence_signals_3x if display_start_date <= d <= end_date_obj]
    if len(convergence_signals_3x_filtered) > 0:
        convergence_prices_sp500 = sp500_3x.loc[convergence_signals_3x_filtered, 'Cumulative_Value'] / 1_000_000
        plt.scatter(convergence_signals_3x_filtered, convergence_prices_sp500, color='#FF1493', s=150, marker='*', 
                   label='Convergence Signal', zorder=5, edgecolors='#C71585', linewidth=2)
    
    plt.axhline(y=total_investment, color='gray', linestyle='--', 
                label=f'Total Investment (₩{total_investment*1_000_000:,.0f})', alpha=0.7)
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value (Million KRW)', fontsize=12)
    plt.title(f'Daily 10,000 KRW Investment in 3x Leveraged Products ({start_date} ~ {end_date}){size_label}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(f'leverage_3x_investment_{start_date}_to_{end_date}.png', dpi=300, bbox_inches='tight')
    print(f"3x Graph saved as 'leverage_3x_investment_{start_date}_to_{end_date}.png'")
    
    # Create 4x Leverage visualization
    plt.figure(figsize=(14, 7))
    
    # Filter data by display date range (create mask for each dataset independently)
    mask_4x_sp500 = (sp500_4x.index >= display_start_date) & (sp500_4x.index <= end_date_obj)
    mask_4x_nasdaq = (nasdaq_4x.index >= display_start_date) & (nasdaq_4x.index <= end_date_obj)
    
    plt.plot(sp500_4x.index[mask_4x_sp500], sp500_4x.loc[mask_4x_sp500, 'Cumulative_Value'] / 1_000_000, 
             label='S&P 500 (4x Leverage)', linewidth=2, color='#2ca02c')
    plt.plot(nasdaq_4x.index[mask_4x_nasdaq], nasdaq_4x.loc[mask_4x_nasdaq, 'Cumulative_Value'] / 1_000_000, 
             label='Nasdaq 100 (4x Leverage)', linewidth=2, color='#d62728')
    
    # Add convergence signal markers for 4x (filtered by display range)
    convergence_signals_4x_filtered = [d for d in convergence_signals_4x if display_start_date <= d <= end_date_obj]
    if len(convergence_signals_4x_filtered) > 0:
        convergence_prices_sp500_4x = sp500_4x.loc[convergence_signals_4x_filtered, 'Cumulative_Value'] / 1_000_000
        convergence_prices_nasdaq_4x = nasdaq_4x.loc[convergence_signals_4x_filtered, 'Cumulative_Value'] / 1_000_000
        plt.scatter(convergence_signals_4x_filtered, convergence_prices_sp500_4x, color='#00FF00', s=150, marker='*', 
                   label='Convergence Signal (4x)', zorder=5, edgecolors='#228B22', linewidth=2)
        plt.scatter(convergence_signals_4x_filtered, convergence_prices_nasdaq_4x, color='#00FF00', s=150, marker='*', 
                   zorder=5, edgecolors='#228B22', linewidth=2)
    
    plt.axhline(y=total_investment, color='gray', linestyle='--', 
                label=f'Total Investment (₩{total_investment*1_000_000:,.0f})', alpha=0.7)
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value (Million KRW)', fontsize=12)
    plt.title(f'Daily 10,000 KRW Investment in 4x Leveraged Products ({start_date} ~ {end_date}){size_label}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(f'leverage_4x_investment_{start_date}_to_{end_date}.png', dpi=300, bbox_inches='tight')
    print(f"4x Graph saved as 'leverage_4x_investment_{start_date}_to_{end_date}.png'")
    
    # Create comparison visualization
    plt.figure(figsize=(14, 7))
    
    # Filter data by display date range (create mask for each dataset independently)
    mask_comparison_sp500_3x = (sp500_3x.index >= display_start_date) & (sp500_3x.index <= end_date_obj)
    mask_comparison_nasdaq_3x = (nasdaq_3x.index >= display_start_date) & (nasdaq_3x.index <= end_date_obj)
    mask_comparison_sp500_4x = (sp500_4x.index >= display_start_date) & (sp500_4x.index <= end_date_obj)
    mask_comparison_nasdaq_4x = (nasdaq_4x.index >= display_start_date) & (nasdaq_4x.index <= end_date_obj)
    
    plt.plot(sp500_3x.index[mask_comparison_sp500_3x], sp500_3x.loc[mask_comparison_sp500_3x, 'Cumulative_Value'] / 1_000_000, 
             label='S&P 500 (3x Leverage)', linewidth=2, color='#1f77b4')
    plt.plot(nasdaq_3x.index[mask_comparison_nasdaq_3x], nasdaq_3x.loc[mask_comparison_nasdaq_3x, 'Cumulative_Value'] / 1_000_000, 
             label='Nasdaq 100 (3x Leverage)', linewidth=2, color='#ff7f0e')
    plt.plot(sp500_4x.index[mask_comparison_sp500_4x], sp500_4x.loc[mask_comparison_sp500_4x, 'Cumulative_Value'] / 1_000_000, 
             label='S&P 500 (4x Leverage)', linewidth=2, color='#2ca02c', linestyle='--')
    plt.plot(nasdaq_4x.index[mask_comparison_nasdaq_4x], nasdaq_4x.loc[mask_comparison_nasdaq_4x, 'Cumulative_Value'] / 1_000_000, 
             label='Nasdaq 100 (4x Leverage)', linewidth=2, color='#d62728', linestyle='--')
    
    # Add convergence signal markers for comparison (use 3x signals, filtered by display range)
    convergence_signals_3x_filtered_comp = [d for d in convergence_signals_3x if display_start_date <= d <= end_date_obj]
    if len(convergence_signals_3x_filtered_comp) > 0:
        convergence_prices_sp500 = sp500_3x.loc[convergence_signals_3x_filtered_comp, 'Cumulative_Value'] / 1_000_000
        plt.scatter(convergence_signals_3x_filtered_comp, convergence_prices_sp500, color='#00FFFF', s=150, marker='*', 
                   label='Convergence Signal', zorder=5, edgecolors='#0088CC', linewidth=2)
    
    plt.axhline(y=total_investment, color='gray', linestyle='--', 
                label=f'Total Investment (₩{total_investment*1_000_000:,.0f})', alpha=0.7)
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value (Million KRW)', fontsize=12)
    plt.title(f'Comparison: 3x vs 4x Leveraged Products ({start_date} ~ {end_date}){size_label}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(f'leverage_comparison_{start_date}_to_{end_date}.png', dpi=300, bbox_inches='tight')
    print(f"Comparison graph saved as 'leverage_comparison_{start_date}_to_{end_date}.png'")
    
    # Create price comparison visualization (3x and 4x with raw prices)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # 3x leverage with raw prices
    ax1_twin = ax1.twinx()
    
    # Filter data by display date range for 3x (create mask for each dataset independently)
    mask_3x_price_sp500 = (sp500_3x.index >= display_start_date) & (sp500_3x.index <= end_date_obj)
    mask_3x_price_nasdaq = (nasdaq_3x.index >= display_start_date) & (nasdaq_3x.index <= end_date_obj)
    mask_3x_price_sp500_prices = (sp500_prices.index >= display_start_date) & (sp500_prices.index <= end_date_obj)
    mask_3x_price_nasdaq_prices = (nasdaq_prices.index >= display_start_date) & (nasdaq_prices.index <= end_date_obj)
    
    ax1.plot(sp500_3x.index[mask_3x_price_sp500], sp500_3x.loc[mask_3x_price_sp500, 'Cumulative_Value'] / 1_000_000, 
             label='S&P 500 (3x Leverage)', linewidth=2, color='#1f77b4')
    ax1.plot(nasdaq_3x.index[mask_3x_price_nasdaq], nasdaq_3x.loc[mask_3x_price_nasdaq, 'Cumulative_Value'] / 1_000_000, 
             label='Nasdaq 100 (3x Leverage)', linewidth=2, color='#ff7f0e')
    
    # Add convergence signals for 3x (filtered by display range)
    convergence_signals_3x_filtered_price = [d for d in convergence_signals_3x if display_start_date <= d <= end_date_obj]
    if len(convergence_signals_3x_filtered_price) > 0:
        convergence_prices_sp500 = sp500_3x.loc[convergence_signals_3x_filtered_price, 'Cumulative_Value'] / 1_000_000
        ax1.scatter(convergence_signals_3x_filtered_price, convergence_prices_sp500, color='#FF1493', s=150, marker='*', 
                   label='Convergence Signal', zorder=5, edgecolors='#C71585', linewidth=2)
    
    # Plot raw prices on secondary axis (filtered by display date range)
    ax1_twin.plot(sp500_prices.index[mask_3x_price_sp500_prices], sp500_prices.loc[mask_3x_price_sp500_prices, sp500_close_col], 
                  label='SPY Price', linewidth=1.5, color='#1f77b4', alpha=0.5, linestyle='--')
    ax1_twin.plot(nasdaq_prices.index[mask_3x_price_nasdaq_prices], nasdaq_prices.loc[mask_3x_price_nasdaq_prices, nasdaq_close_col], 
                  label='QQQ Price', linewidth=1.5, color='#ff7f0e', alpha=0.5, linestyle='--')
    
    ax1.set_xlabel('Date', fontsize=11)
    ax1.set_ylabel('Leverage Investment Value (Million KRW)', fontsize=11)
    ax1_twin.set_ylabel('Stock Price (USD)', fontsize=11)
    ax1.set_title(f'3x Leverage Investment with Price Comparison ({start_date} ~ {end_date}){size_label}', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1_twin.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 4x leverage with raw prices
    ax2_twin = ax2.twinx()
    
    # Filter data by display date range for 4x (create mask for each dataset independently)
    mask_4x_price_sp500 = (sp500_4x.index >= display_start_date) & (sp500_4x.index <= end_date_obj)
    mask_4x_price_nasdaq = (nasdaq_4x.index >= display_start_date) & (nasdaq_4x.index <= end_date_obj)
    mask_4x_price_sp500_prices = (sp500_prices.index >= display_start_date) & (sp500_prices.index <= end_date_obj)
    mask_4x_price_nasdaq_prices = (nasdaq_prices.index >= display_start_date) & (nasdaq_prices.index <= end_date_obj)
    
    ax2.plot(sp500_4x.index[mask_4x_price_sp500], sp500_4x.loc[mask_4x_price_sp500, 'Cumulative_Value'] / 1_000_000, 
             label='S&P 500 (4x Leverage)', linewidth=2, color='#2ca02c')
    ax2.plot(nasdaq_4x.index[mask_4x_price_nasdaq], nasdaq_4x.loc[mask_4x_price_nasdaq, 'Cumulative_Value'] / 1_000_000, 
             label='Nasdaq 100 (4x Leverage)', linewidth=2, color='#d62728')
    
    # Add convergence signals for 4x (filtered by display range)
    convergence_signals_4x_filtered_price = [d for d in convergence_signals_4x if display_start_date <= d <= end_date_obj]
    if len(convergence_signals_4x_filtered_price) > 0:
        convergence_prices_sp500_4x = sp500_4x.loc[convergence_signals_4x_filtered_price, 'Cumulative_Value'] / 1_000_000
        ax2.scatter(convergence_signals_4x_filtered_price, convergence_prices_sp500_4x, color='#00FF00', s=150, marker='*', 
                   label='Convergence Signal', zorder=5, edgecolors='#228B22', linewidth=2)
    
    # Plot raw prices on secondary axis (filtered by display date range)
    ax2_twin.plot(sp500_prices.index[mask_4x_price_sp500_prices], sp500_prices.loc[mask_4x_price_sp500_prices, sp500_close_col], 
                  label='SPY Price', linewidth=1.5, color='#2ca02c', alpha=0.5, linestyle='--')
    ax2_twin.plot(nasdaq_prices.index[mask_4x_price_nasdaq_prices], nasdaq_prices.loc[mask_4x_price_nasdaq_prices, nasdaq_close_col], 
                  label='QQQ Price', linewidth=1.5, color='#d62728', alpha=0.5, linestyle='--')
    
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('Leverage Investment Value (Million KRW)', fontsize=11)
    ax2_twin.set_ylabel('Stock Price (USD)', fontsize=11)
    ax2.set_title(f'4x Leverage Investment with Price Comparison ({start_date} ~ {end_date}){size_label}', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2_twin.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'leverage_with_prices_{start_date}_to_{end_date}.png', dpi=300, bbox_inches='tight')
    print(f"Price comparison graph saved as 'leverage_with_prices_{start_date}_to_{end_date}.png'")
    
    # Create difference visualization (Nasdaq - S&P500 for 3x and 4x)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Filter data by display date range (create mask for each dataset independently)
    mask_diff_sp500_3x = (sp500_3x.index >= display_start_date) & (sp500_3x.index <= end_date_obj)
    mask_diff_nasdaq_3x = (nasdaq_3x.index >= display_start_date) & (nasdaq_3x.index <= end_date_obj)
    mask_diff_sp500_4x = (sp500_4x.index >= display_start_date) & (sp500_4x.index <= end_date_obj)
    mask_diff_nasdaq_4x = (nasdaq_4x.index >= display_start_date) & (nasdaq_4x.index <= end_date_obj)
    
    # 3x Leverage: Nasdaq(3x) - S&P500(3x)
    diff_3x = nasdaq_3x.loc[mask_diff_nasdaq_3x, 'Cumulative_Value'] / 1_000_000 - sp500_3x.loc[mask_diff_sp500_3x, 'Cumulative_Value'] / 1_000_000
    
    ax1.plot(sp500_3x.index[mask_diff_sp500_3x], diff_3x, linewidth=2.5, color='#d62728', label='Nasdaq(3x) - S&P500(3x)')
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.7, label='Zero Line')
    ax1.fill_between(sp500_3x.index[mask_diff_sp500_3x], diff_3x, 0, where=(diff_3x >= 0), alpha=0.3, color='#2ca02c', label='Nasdaq > S&P500')
    ax1.fill_between(sp500_3x.index[mask_diff_sp500_3x], diff_3x, 0, where=(diff_3x < 0), alpha=0.3, color='#1f77b4', label='S&P500 > Nasdaq')
    
    ax1.set_xlabel('Date', fontsize=11)
    ax1.set_ylabel('Value Difference (Million KRW)', fontsize=11)
    ax1.set_title(f'3x Leverage: Nasdaq(3x) - S&P500(3x) ({start_date} ~ {end_date}){size_label}', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 4x Leverage: Nasdaq(4x) - S&P500(4x)
    diff_4x = nasdaq_4x.loc[mask_diff_nasdaq_4x, 'Cumulative_Value'] / 1_000_000 - sp500_4x.loc[mask_diff_sp500_4x, 'Cumulative_Value'] / 1_000_000
    
    ax2.plot(sp500_4x.index[mask_diff_sp500_4x], diff_4x, linewidth=2.5, color='#ff7f0e', label='Nasdaq(4x) - S&P500(4x)')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.7, label='Zero Line')
    ax2.fill_between(sp500_4x.index[mask_diff_sp500_4x], diff_4x, 0, where=(diff_4x >= 0), alpha=0.3, color='#2ca02c', label='Nasdaq > S&P500')
    ax2.fill_between(sp500_4x.index[mask_diff_sp500_4x], diff_4x, 0, where=(diff_4x < 0), alpha=0.3, color='#1f77b4', label='S&P500 > Nasdaq')
    
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('Value Difference (Million KRW)', fontsize=11)
    ax2.set_title(f'4x Leverage: Nasdaq(4x) - S&P500(4x) ({start_date} ~ {end_date}){size_label}', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'leverage_difference_{start_date}_to_{end_date}.png', dpi=300, bbox_inches='tight')
    print(f"Difference graph saved as 'leverage_difference_{start_date}_to_{end_date}.png'")
    
    plt.show()


if __name__ == "__main__":
    main()
