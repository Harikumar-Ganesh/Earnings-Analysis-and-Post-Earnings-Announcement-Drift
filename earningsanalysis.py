import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# This function finds the stock prices for a given ticker symbol between beginning of year to October 31, 2024
def get_stock_prices(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    data = data[['Close']].copy()
    data['Return'] = data['Close'].pct_change()
    data.reset_index(inplace=True)
    data.columns = data.columns.get_level_values(0)
    data.columns = ['Date', 'Close', 'Return']
    return data

# This function calculates the surprise percentage for earnings data which is found in a local CSV file
def calculate_surprise(csv_path):
    earnings = pd.read_csv(csv_path)
    earnings['Surprise Percentage'] = (earnings['Actual_EPS'] - earnings['Expected_EPS']) / earnings['Expected_EPS'].abs()
    earnings['Surprise Percentage'] = earnings['Surprise Percentage'] * 100
    return earnings

# This function utilizes aggregate market data from a user-specified benchmark to analyze expected and actual EPS based on the real market conditions
def market_data(start_date, end_date, index_ticker='^GSPC'):
    benchmark = yf.download(index_ticker, start=start_date, end=end_date, progress=False)
    benchmark = benchmark[['Close']].copy()
    benchmark['Benchmark_Return'] = benchmark['Close'].pct_change()
    benchmark.reset_index(inplace=True)
    benchmark.columns = benchmark.columns.get_level_values(0)
    benchmark = benchmark[['Date', 'Benchmark_Return']]
    return benchmark

# This calculates abnormal returns based on ticker and business days
def calculate_abnormal_returns(ticker, announcement_date, benchmark='^GSPC', window_bf=10, window_af=10):
    announcement = pd.to_datetime(announcement_date)
    start = announcement - pd.Timedelta(days=window_bf + 30) 
    end = announcement + pd.Timedelta(days=window_af + 30)    
    stock_data = get_stock_prices(ticker, start, end)
    benchmark_data = market_data(start, end, index_ticker=benchmark)  
    merged_dates = pd.merge(stock_data, benchmark_data, on="Date")
    merged_dates["Abnormal_Return"] = merged_dates["Return"] - merged_dates["Benchmark_Return"]
    merged_dates['Days_From_Announcement'] = (merged_dates['Date'] - announcement).dt.days
    event_window = merged_dates[(merged_dates['Days_From_Announcement'] >= -window_bf) & (merged_dates['Days_From_Announcement'] <= window_af)].copy()
    return event_window

# This function analyzes all earnings events from the CSV and calculates CAR for each event using the specified benchmark
def analyze_earnings(csv_path, benchmark='^GSPC'):
    earnings = calculate_surprise(csv_path)
    results = []
    for index, row in earnings.iterrows():
        ticker = row['Ticker']
        date = row["Earnings_Date"]
        surprise = row['Surprise Percentage']
        print(f"Processing {ticker} on {date} (vs {benchmark})")
        try:
            event_data = calculate_abnormal_returns(ticker, date, benchmark=benchmark, window_bf=10, window_af=10)
            c_a_r = event_data['Abnormal_Return'].sum() * 100
            results.append({
                'Ticker': ticker,
                'Date': date,
                'Surprise Percentage': surprise,
                'Benchmark': benchmark,
                'CAR': c_a_r
            })
        except Exception as e:
            print(f"Error: {e}")
        
    results_data = pd.DataFrame(results)
    return results_data

# User input section: allows user to select which benchmark index to compare stocks against
print("\n" + "="*60)
print("BENCHMARK SELECTION")
print("="*60)
print("Common benchmarks:")
print("  ^GSPC - S&P 500 (broad market)")
print("  ^IXIC - NASDAQ Composite (tech-heavy)")
print("  ^DJI  - Dow Jones Industrial Average")
print("  XLK   - Technology Select Sector SPDR")
print("  XLF   - Financial Select Sector SPDR")
print("  XLV   - Health Care Select Sector SPDR")
print("  XLE   - Energy Select Sector SPDR")
print("  XLI   - Industrial Select Sector SPDR")
print()

benchmark_ticker = input("Enter benchmark ticker (press Enter for default ^GSPC): ").strip().upper()
if not benchmark_ticker:
    benchmark_ticker = '^GSPC'

print(f"\nUsing benchmark: {benchmark_ticker}")
print("="*60 + "\n")

# Load and display earnings data
print("Testing Earnings function:")
earnings_data = calculate_surprise('earningsanalysis_data.csv')
print(earnings_data.head(60))
print(f"Total events: {len(earnings_data)}")

# Analyze all 60 earnings events with the chosen benchmark
print(f"\nAnalyzing all earnings events against {benchmark_ticker}...")
all_results = analyze_earnings('earningsanalysis_data.csv', benchmark=benchmark_ticker)

print(all_results.head(60))
print(f"Total events analyzed: {len(all_results)}")
print(f"Average CAR: {all_results['CAR'].mean():.2f}%")

# Display overall statistics
print("\n" + "="*60)
print("ANALYSIS RESULTS")
print("="*60)
print("--- Overall Statistics ---")
print(f"Total events analyzed: {len(all_results)}")
print(f"Average CAR: {all_results['CAR'].mean():.2f}%")
print(f"Median CAR: {all_results['CAR'].median():.2f}%")
print(f"Std Dev of CAR: {all_results['CAR'].std():.2f}%")

# Compare beats vs misses
print("\n--- Beats vs Misses ---")
beats = all_results[all_results['Surprise Percentage'] > 0]
misses = all_results[all_results['Surprise Percentage'] < 0]
print(f"Number of beats: {len(beats)}")
print(f"Average CAR for beats: {beats['CAR'].mean():.2f}%")
print(f"\nNumber of misses: {len(misses)}")
print(f"Average CAR for misses: {misses['CAR'].mean():.2f}%")

# Show top and bottom performers
print("\n--- Top 5 Best Performers ---")
top5 = all_results.nlargest(5, 'CAR')[['Ticker', 'Date', 'Surprise Percentage', 'CAR']]
print(top5.to_string(index=False))

print("\n--- Top 5 Worst Performers ---")
bottom5 = all_results.nsmallest(5, 'CAR')[['Ticker', 'Date', 'Surprise Percentage', 'CAR']]
print(bottom5.to_string(index=False))

# Calculate correlation between surprise percentage and CAR
correlation = all_results['Surprise Percentage'].corr(all_results['CAR'])
print(f"\n--- Correlation Analysis ---")
print(f"Correlation between Surprise % and CAR: {correlation:.3f}")

# Create visualizations
print("\nCreating visualizations...")

# Graph 1: Scatter plot showing relationship between earnings surprise and cumulative abnormal return
plt.figure(figsize=(10, 6))
plt.scatter(all_results['Surprise Percentage'], all_results['CAR'], alpha=0.6)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.axvline(x=0, color='red', linestyle='--', linewidth=1)
plt.xlabel('Earnings Surprise (%)')
plt.ylabel('Cumulative Abnormal Return (%)')
plt.title(f"Earnings Surprise vs Stock Return (vs {benchmark_ticker})")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("surprise_vs_car.png")
print("Saved: surprise_vs_car.png")

# Graph 2: Bar chart comparing average CAR for beats vs misses
plt.figure(figsize=(8, 6))
categories = ['Beats', 'Misses']
avg_cars = [beats['CAR'].mean(), misses['CAR'].mean()]
colors = ['green' if x > 0 else 'red' for x in avg_cars]
plt.bar(categories, avg_cars, color=colors, alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
plt.ylabel('Average CAR (%)')
plt.title(f'Average CAR: Beats vs Misses (vs {benchmark_ticker})')
plt.tight_layout()
plt.savefig('beats_vs_misses.png')
print("Saved: beats_vs_misses.png")

print("\nVisualization complete!")
print("="*60)
