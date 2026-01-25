# Earnings-Analysis-and-Post-Earnings-Announcement-Drift
Earnings Analysis and Post-Earnings Announcement Drift (PEAD) visualized using Python
 ## Overview

This project is a tool to help understand and visualize post-earnings announcement drift (PEAD) using real data. It analyzes 60 earnings events across 15 stocks and compares their performance to a user-selected ETF or index.

It uses cumulative abnormal return (CAR) to measure how stocks behave around earnings announcements. The scatter plot shows all events with their surprise percentages and CAR, which makes it easier to see patterns and outliers. The bar chart compares the average CAR for earnings beats versus earnings misses, helping show whether positive surprises tend to be followed by stronger performance.

I believe this tool can be useful for anyone who wants to see PEAD in action or compare how different benchmarks affect the results.

## Motivation
For as long as I can remember, I’ve been interested in computers. I always wanted to be on one (whether it was playing games on the Nickelodeon website or getting through those dreaded Study Island assignments), but I never really understood what computers could actually be used for beyond that.

Now, as a junior in high school interested in finance and data analysis, I wanted to combine my interest in computers with my interest in markets to better understand how post-earnings announcement drift (PEAD) works. Along the way, I also wanted to build something practical (a tool that other people interested in finance could use or modify).

More than anything, this project was about seeing how concepts from math and statistics can be used to explain real financial behavior, and learning how those ideas actually work by implementing them myself.

## Research Question
In this project, I tested whether stocks that beat earnings expectations tended to experience stronger returns than stocks that missed expectations. I did this by examining the visual relationship between earnings surprise percentage and CAR, and by evaluating whether the data showed any evidence of PEAD.

## Data

The data I used was expected earnings per share (analyst estimates) and actual earnings per share, which I collected from Yahoo Finance. I wanted to use accurate, already-published data, so I selected earnings data from Q4 2024 through Q3 2025.

I collected this data for 15 different stocks across a variety of sectors to get a broader view of the market rather than focusing on a single industry. Since I used four quarters of earnings data for each of the 15 stocks, the dataset contained a total of 60 data points (four per ticker).

## Methodology
1. Returns:
For each stock, I collected daily closing price data using the yfinance API. I calculated daily returns by measuring the percent change in price from one trading day to the next.

2. Benchmark:
The user can select a specific index or ETF. The returns of that index or ETF are then used as the market benchmark, since they represent the performance of broader markets or individual sectors.

3. Abnormal Returns:
To see how a stock moved relative to the selected benchmark, I subtracted the benchmark’s return from the stock’s return.

4. Event Window:
To get a comprehensive view of stock movement, I analyzed returns from 10 days before the earnings announcement to 10 days after the announcement. This window is important because it allows me to examine whether price behavior around earnings shows any evidence of PEAD.

5. Cumulative Abnormal Return (CAR):
I calculated cumulative abnormal return (CAR) by adding up abnormal returns over the -10 to +10 day event window for each earnings event (one date for one stock). This gave me a single value per event, which made it easier to compare performance across all stocks and announcement dates.

6. Visualizations:
To better understand my results, I created two graphs. The first is a scatter plot showing earnings surprise percentage versus CAR for all 60 events, which makes it easier to see overall trends and outliers. The second is a bar chart comparing the average CAR for beats (positive earnings surprise, where actual earnings exceeded expectations) and misses (negative earnings surprise, where actual earnings were lower than expected). This helps determine whether positive surprises tend to be associated with stronger performance.


## Results and Interpretation


This tool creates two visualizations to help interpret the relationship between earnings surprises and post-announcement performance.

The first visualization (a scatter plot) helps users see whether larger surprises tend to be associated with higher returns and makes it easier to identify outliers.

The second visualization (a bar graph) compares the average performance of positive surprises versus negative surprises to help determine whether earnings beats are associated with stronger post-announcement performance relative to the selected benchmark.

Together, these graphs allow users to explore whether PEAD appears under different benchmark conditions and across different sets of tickers (by modifying the input data as described in the run instructions).


## Sample Output

Below are example visualizations generated using the S&P 500 (^GSPC) as the benchmark:

### 1: Earnings Surprise vs Cumulative Abnormal Return (Scatter Plot)
<img width="1000" height="600" alt="surprise_vs_car" src="https://github.com/user-attachments/assets/d89c876d-0f29-4931-ad5a-791cb22b19c4" />

This scatter plot shows the relationship between earnings surprise percentage and CAR for all 60 events. Points in the upper-right quadrant represent stocks that beat expectations and outperformed the market, while points in the lower-left represent misses that underperformed.

### 2: Average CAR: Beats vs Misses
<img width="800" height="600" alt="beats_vs_misses" src="https://github.com/user-attachments/assets/b16e68c2-781d-41ea-bc83-5dd037c75b43" />

This bar chart compares the average CAR for earnings beats (+0.42%) versus misses (-3.84%). The results suggest that markets continue to drift in the direction of the earnings surprise, providing evidence of post-earnings announcement drift.

## Note: These results are based on the included dataset (Q4 2024 - Q3 2025). Your results may vary if you modify the CSV with different stocks, dates, or use a different benchmark.
## Interactive Visualizations

In addition to static PNG images, the tool generates **interactive HTML visualizations** using Plotly.

**Features of interactive charts:**
- Hover over any data point to see the ticker symbol and announcement date
- Zoom in/out to focus on specific regions
- Pan across the chart
- Download customized views as PNG
- Better for exploring outliers and patterns

**To use:** Simply open `surprise_vs_car_interactive.html`in your web browser after running the tool.

This interactive chart are especially useful for:
- Identifying which specific stocks drove extreme returns
- Comparing multiple earnings events for the same company
- Presenting findings in an engaging, exploratory format

## Limitations


There are several limitations and assumptions in this project. One major assumption is that ETFs and indices behave like the overall market. In reality, no ETF or index can perfectly represent the market because it does not include every asset.

From an analytical standpoint, one limitation is that I used simple returns instead of log returns. Simple returns are easier to calculate and interpret, but log returns are often preferred in financial research because they handle compounding more accurately, they are closer to normal distribution (bell shape) and reduce influence of outliers (extreme values).

Additionally, since the dataset only includes 60 events, the sample size is small by financial research standards, which means the results may not be fully reliable.

## What I learned

I learned a lot from building this project. I learned how surprise percentage is calculated, how abnormal return is calculated and why it matters, and how cumulative abnormal return can be used in different contexts to provide evidence for Post-Earnings Announcement Drift. More than anything, I learned how important graphs and visualizations are in finance and analytics because they make data easier to understand and reveal trends, changes, outliers, and patterns in behavior.


## How to Run

Install the required libraries:
```bash
pip install yfinance pandas matplotlib plotly numpy
```
If this does not work, try:
 ```bash
pip3 install yfinance pandas matplotlib plotly numpy
```
Download both `earningsanalysis.py` and `earningsanalysis_data.csv`.

Place both files in the same folder.

Run the Python file:
```bash
python earningsanalysis.py
```

When prompted, select a benchmark index (or press Enter for S&P 500).

The program will generate **four output files**:
- `surprise_vs_car.png` (static scatter plot)
- `surprise_vs_car_interactive.html` (interactive scatter plot - **hover to see ticker and date**)
- `beats_vs_misses.png` (static bar chart)

**To view interactive charts:** Open the `.html` files in any web browser. You can hover over data points to see details, zoom in/out, and explore the data.

**Optional:** The included CSV contains earnings data from Q4 2024 to Q3 2025.
If you want to analyze different stocks, dates, or time periods, you can edit the CSV file with new tickers, earnings dates, expected EPS, and actual EPS. The tool will still work without changing the code.


## Next Steps:
   ## Completed!
 - Implement Logarithm Based Calculations to make the return more accurate and effective
## Yet to add! 
 - Implement Sector Specific Benchmarks (Ex. JPM vs XLF; AAPL vs XLK; JNJ vs XLV)

 - Implement t-testing to solidify whether data is just "noise" or statistically relevant
