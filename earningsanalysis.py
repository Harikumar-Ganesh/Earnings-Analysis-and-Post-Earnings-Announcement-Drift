
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

ticker = yf.Ticker("AAPL")
# This function calculates the surprise percentage for earnings data which is found in a local CSV file
def calculate_surprise(csv_path):
    earnings=pd.read_csv(csv_path)
    earnings['Surprise Percentage'] = (earnings['Actual_EPS'] - earnings['Expected_EPS']) / earnings['Expected_EPS'].abs()
    earnings['Surprise Percentage']=earnings['Surprise Percentage'] * 100
    return earnings
# This function utlizes aggregate market data from the S&P 500 to analyze expected and actual EPS based on the real market conditions
def market_data(start_date,end_date):
    sp500 = yf.download("^GSPC", start=start_date, end=end_date, progress=False)
    sp500 = sp500[['Close']].copy()
    sp500['SP500_Return'] = sp500['Close'].pct_change()
    sp500.reset_index(inplace=True)
    sp500.columns = sp500.columns.get_level_values(0)
    sp500 = sp500[['Date', 'SP500_Return']]
    return sp500
#This calculates abnormal returns based on ticker and business days
def calculate_abnormal_returns(ticker, announcement_date, window_bf=10, window_af=10):
    announcement = pd.to_datetime(announcement_date)
    start = announcement - pd.Timedelta(days=window_bf + 30) 
    end = announcement + pd.Timedelta(days=window_af + 30)    
    stock_data = get_stock_prices(ticker, start, end)
    sp500_data = market_data(start, end)  
    merged_dates = pd.merge(stock_data, sp500_data, on="Date")
    merged_dates["Abnormal_Return"] = merged_dates["Return"] - merged_dates["SP500_Return"]
    merged_dates['Days_From_Announcement'] = (merged_dates['Date'] - announcement).dt.days
    event_window = merged_dates[(merged_dates['Days_From_Announcement'] >= -window_bf) & (merged_dates['Days_From_Announcement'] <= window_af)].copy()
    return event_window
def analyze_earnings(csv_path):
    earnings=calculate_surprise(csv_path)
    results=[]
    for index, row in earnings.iterrows():
        ticker=row['Ticker']
        date=row["Earnings_Date"]
        surprise=row['Surprise Percentage']
        print(f"Processing {ticker} on {date}")
        try:
            event_data=calculate_abnormal_returns(ticker,date,window_bf=10,window_af=10)
            c_a_r=event_data['Abnormal_Return'].sum()*100
            results.append({
            'Ticker': ticker,
            'Date': date,
            'Surprise Percentage': surprise,
            'CAR': c_a_r })
        except Exception as e:
            print(f"Error: {e}")
        
    results_data=pd.DataFrame(results)
    return results_data
     
print("Testing Earnings function:")
earnings_data=calculate_surprise('earningsanalysis_data.csv')
print(earnings_data.head(60))
print(f"Total events:{len(earnings_data)}")
# Test abnormal returns
print("Testing abnormal returns for AAPL...")

aapl_event = calculate_abnormal_returns("AAPL", "2025-10-30", window_bf=10, window_af=10)

print(aapl_event[['Date', 'Days_From_Announcement', 'Abnormal_Return']])
# Analyze all 60 earnings events
print("Analyzing all earnings events...")
all_results = analyze_earnings('earningsanalysis_data.csv')
positive_results=all_results[all_results["CAR"]>0]
negative_results=all_results[all_results["CAR"]<0]
print(all_results.head(60))
print(f"Total events analyzed: {len(all_results)}")
print(f"Average CAR: {all_results['CAR'].mean():.2f}%")
print("--- Overall Statistics ---")
print(f"Total events analyzed: {len(all_results)}")
print(f"Average CAR: {all_results['CAR'].mean():.2f}%")
print(f"Median CAR: {all_results['CAR'].median():.2f}%")
print(f"Std Dev of CAR: {all_results['CAR'].std():.2f}%")
print("--- Beats vs Misses ---")
beats = all_results[all_results['Surprise Percentage'] > 0]
misses = all_results[all_results['Surprise Percentage'] < 0]
print(f"Number of beats: {len(beats)}")
print(f"Average CAR for beats: {beats['CAR'].mean():.2f}%")
print(f"\nNumber of misses: {len(misses)}")
print(f"Average CAR for misses: {misses['CAR'].mean():.2f}%")
print("--- Top 5 Best Performers ---")
top5 = all_results.nlargest(5, 'CAR')[['Ticker', 'Date', 'Surprise Percentage', 'CAR']]
print(top5.to_string(index=False))
print("--- Top 5 Worst Performers ---")
bottom5 = all_results.nsmallest(5, 'CAR')[['Ticker', 'Date', 'Surprise Percentage', 'CAR']]
print(bottom5.to_string(index=False))
correlation = all_results['Surprise Percentage'].corr(all_results['CAR'])
print(f"\--- Correlation Analysis ---")
print(f"Correlation between Surprise % and CAR: {correlation:.3f}")
# Graph #1: Average CAR vs Surprise Percentage
plt.figure(figsize=(10,6))
plt.scatter(all_results['Surprise Percentage'],all_results['CAR'],alpha=0.6)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.axvline(x=0, color='red', linestyle='--', linewidth=1)
plt.xlabel('Earnings Surprise (%)')
plt.ylabel('Cumulative Abnormal Return (%)')
plt.title("Earning Surprise vs Stock Return")
plt.grid(True, alpha=0.6)
plt.tight_layout()
plt.savefig("Graph_1.png")
print("Graph 1 Saved")
# Graph #2: Beats vs Misses
plt.figure(figsize=(8, 6))
categories = ['Beats', 'Misses']
avg_cars = [beats['CAR'].mean(), misses['CAR'].mean()]
colors = ['green' if x > 0 else 'red' for x in avg_cars]
plt.bar(categories, avg_cars, color=colors, alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
plt.ylabel('Average CAR (%)')
plt.title('Average CAR: Beats vs Misses')
plt.tight_layout()
plt.savefig('beats_vs_misses.png')
print("Saved: beats_vs_misses.png")
print("Visualization Complete!")
