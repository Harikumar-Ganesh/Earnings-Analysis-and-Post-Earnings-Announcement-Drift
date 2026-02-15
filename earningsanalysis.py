import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# This function finds the stock prices for a given ticker symbol
def get_stock_prices(ticker, start_date, end_date, use_log_returns=True):
    """
    Pull stock prices and calculate returns.
    
    Parameters:
    - use_log_returns: if True, use log returns; if False, use simple returns
    """
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    data = data[['Close']].copy()
    
    if use_log_returns:
        data['Return'] = np.log(data['Close'] / data['Close'].shift(1))
    else:
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
#Bootstrapping function to test validity of CAR data
def bootstrap_CAR(data,iterations=10000):
    means=[]
    for i in range (iterations):
        sample=np.random.choice(data, size=len(data), replace= True)
        means.append(sample.mean())
    car_mean=np.mean(data)
    ci_upper=np.percentile(means, 97.5)
    ci_lower=np.percentile(means,2.5)
    if car_mean>0:
        p_value=(np.sum(np.array(means)<=0)/iterations)
    else:
        p_value=(np.sum(np.array(means)>=0)/iterations)
    return car_mean,(ci_lower,ci_upper),p_value
#Bootstrapping function to test differences
def bootstrap_difference(d1, d2, iterations=10000):
    differences=[]
    for i in range(iterations):
        s1=np.random.choice(d1,size=len(d1),replace=True)
        s2=np.random.choice(d2, size=len(d2), replace= True)
        differences.append(s1.mean()-s2.mean())
    mean_difference=np.mean(d1) - np.mean(d2)
    ci_upperdiff=np.percentile(differences,97.5)
    ci_lowerdiff=np.percentile(differences,2.5)
    p_value = np.sum(np.array(differences) <= 0) / iterations
    return mean_difference, (ci_lowerdiff, ci_upperdiff), p_value 


# This function utilizes aggregate market data from a user-specified benchmark
def market_data(start_date, end_date, index_ticker='^GSPC', use_log_returns=True):
 
    benchmark = yf.download(index_ticker, start=start_date, end=end_date, progress=False)
    benchmark = benchmark[['Close']].copy()
    
    if use_log_returns:
        benchmark['Benchmark_Return'] = np.log(benchmark['Close'] / benchmark['Close'].shift(1))
    else:
        benchmark['Benchmark_Return'] = benchmark['Close'].pct_change()
    
    benchmark.reset_index(inplace=True)
    benchmark.columns = benchmark.columns.get_level_values(0)
    benchmark = benchmark[['Date', 'Benchmark_Return']]
    return benchmark

# This calculates abnormal returns based on ticker and business days
def calculate_abnormal_returns(ticker, announcement_date, benchmark='^GSPC', window_bf=10, window_af=10, use_log_returns=True):
    announcement = pd.to_datetime(announcement_date)
    start = announcement - pd.Timedelta(days=window_bf + 30) 
    end = announcement + pd.Timedelta(days=window_af + 30)    
    
    stock_data = get_stock_prices(ticker, start, end, use_log_returns=use_log_returns)
    benchmark_data = market_data(start, end, index_ticker=benchmark, use_log_returns=use_log_returns)  
    
    merged_dates = pd.merge(stock_data, benchmark_data, on="Date")
    merged_dates["Abnormal_Return"] = merged_dates["Return"] - merged_dates["Benchmark_Return"]
    merged_dates['Days_From_Announcement'] = (merged_dates['Date'] - announcement).dt.days
    
    event_window = merged_dates[
        (merged_dates['Days_From_Announcement'] >= -window_bf) & 
        (merged_dates['Days_From_Announcement'] <= window_af)
    ].copy()
    
    return event_window

# This function analyzes all earnings events from the CSV and calculates CAR for each event
def analyze_earnings(csv_path, benchmark='^GSPC', use_log_returns=True):
    earnings = calculate_surprise(csv_path)
    results = []
    
    for index, row in earnings.iterrows():
        ticker = row['Ticker']
        date = row["Earnings_Date"]
        surprise = row['Surprise Percentage']
        print(f"Processing {ticker} on {date} (vs {benchmark})")
        
        try:
            event_data = calculate_abnormal_returns(
                ticker, date, 
                benchmark=benchmark, 
                window_bf=10, 
                window_af=10,
                use_log_returns=use_log_returns
            )
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

# User selects return type
print("\nReturn calculation method:")
print("  1 - Log returns (recommended for academic rigor)")
print("  2 - Simple returns (easier to interpret)")
return_choice = input("Enter choice (press Enter for log returns): ").strip()

use_log_returns = True if return_choice == '1' else False
return_type = "log returns" if use_log_returns else "simple returns"
print(f"Using: {return_type}")
print("="*60 + "\n")


print(f"Analyzing all earnings events against {benchmark_ticker} using {return_type}...")
all_results = analyze_earnings('earningsanalysis_data.csv', benchmark=benchmark_ticker, use_log_returns=use_log_returns)
# Analysis
print("\n" + "="*60)
print(f"ANALYSIS RESULTS (using {return_type.upper()})")
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

# Calculate correlation
correlation = all_results['Surprise Percentage'].corr(all_results['CAR'])
print(f"\n--- Correlation Analysis ---")
print(f"Correlation between Surprise % and CAR: {correlation:.3f}")


print("\nCreating visualizations...")

# Interactive scatter plot
fig = px.scatter(
    all_results, 
    x='Surprise Percentage', 
    y='CAR', 
    hover_data=['Ticker', 'Date'], 
    title=f'Earnings Surprise vs Stock Return (vs {benchmark_ticker}, {return_type})',
    labels={
        'Surprise Percentage': 'Earnings Surprise (%)', 
        'CAR': 'Cumulative Abnormal Return (%)'
    },
    opacity=0.6
)
fig.add_hline(y=0, line_dash="dash", line_color="red", line_width=1)
fig.add_vline(x=0, line_dash="dash", line_color="red", line_width=1)
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.write_html("surprise_vs_car_interactive.html")
print("Saved: surprise_vs_car_interactive.html")

# Static scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(all_results['Surprise Percentage'], all_results['CAR'], alpha=0.6)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.axvline(x=0, color='red', linestyle='--', linewidth=1)
plt.xlabel('Earnings Surprise (%)')
plt.ylabel('Cumulative Abnormal Return (%)')
plt.title(f"Earnings Surprise vs Stock Return (vs {benchmark_ticker}, {return_type})")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("surprise_vs_car.png")
print("Saved: surprise_vs_car.png")

# Bar chart
plt.figure(figsize=(8, 6))
categories = ['Beats', 'Misses']
avg_cars = [beats['CAR'].mean(), misses['CAR'].mean()]
colors = ['green' if x > 0 else 'red' for x in avg_cars]
plt.bar(categories, avg_cars, color=colors, alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
plt.ylabel('Average CAR (%)')
plt.title(f'Average CAR: Beats vs Misses (vs {benchmark_ticker}, {return_type})')
plt.tight_layout()
plt.savefig('beats_vs_misses.png')
print("Saved: beats_vs_misses.png")

print("\n" + "="*60)
print("Bootstrap Analysis of data (10,000 Iterations)")
print("\n" + "="*60)
# Bootstrap for beats
beats_mean, beats_ci, beats_p = bootstrap_CAR(beats['CAR'].values)
print("Beats:")
print(f"  Mean CAR: {beats_mean:.2f}%")
print(f"  95% CI: [{beats_ci[0]:.2f}%, {beats_ci[1]:.2f}%]")
print(f"  P-value: {beats_p:.4f}")
if beats_p < 0.05:
    print("Statistically significant at 5% level")
else:
    print("Not statistically significant")

# Bootstrap for misses
misses_mean, misses_ci, misses_p = bootstrap_CAR(misses['CAR'].values)
print("\nMisses:")
print(f"  Mean CAR: {misses_mean:.2f}%")
print(f"  95% CI: [{misses_ci[0]:.2f}%, {misses_ci[1]:.2f}%]")
print(f"  P-value: {misses_p:.4f}")
if misses_p < 0.05:
    print("Statistically significant at 5% level")
else:
    print("Not statistically significant")

# Bootstrap for difference (beats - misses)
diff_mean, diff_ci, diff_p = bootstrap_difference(beats['CAR'].values, misses['CAR'].values)
print("\nDifference (Beats - Misses):")
print(f"  Mean difference: {diff_mean:.2f}%")
print(f"  95% CI: [{diff_ci[0]:.2f}%, {diff_ci[1]:.2f}%]")
print(f"  P-value: {diff_p:.4f}")
if diff_p < 0.05:
    print("Beats significantly outperform misses")
else:
    print("Difference not statistically significant")

print("\n" + "="*60)
print("Bootstrap analysis complete!")
