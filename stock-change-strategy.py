import streamlit as st
import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5y", interval="1mo")
    return data

def calculate_threshold_exceeds(data, threshold):
    if data.empty:
        return None, 0
    data['Monthly_Change'] = (data['Close'] - data['Open']) / data['Open'] * 100
    exceeds_count = (data['Monthly_Change'].abs() > threshold).sum()
    max_change = data['Monthly_Change'].max()
    min_change = data['Monthly_Change'].min()
    if (abs(max_change) > abs(min_change)):
        return max_change, exceeds_count
    else:
        return min_change, exceeds_count

st.title("Stock Change Analysis")

# User input for tickers
tickers_input = st.text_input("Enter stock tickers:", "AAPL,GOOGL,MSFT")
tickers = [ticker.strip() for ticker in tickers_input.split(',')]

# User input for threshold
threshold = st.number_input("Enter threshold for change (%):", value=10.0)

# Add a button to trigger the analysis
if st.button("Run Analysis"):
    # Create a DataFrame to store results
    results = []

    for ticker in tickers:
        data = fetch_stock_data(ticker)
        max_change, exceeds_count = calculate_threshold_exceeds(data, threshold)
        if max_change is not None:
            results.append({
                'Ticker': ticker,
                'Max Monthly Change (%)': round(max_change, 2),
                f'Times Exceeded {threshold}%': exceeds_count
            })
        else:
            st.warning(f"No data available for {ticker}")

    if results:
        # Create and display the results table
        results_df = pd.DataFrame(results)
        
        # Sort the DataFrame by the 'Times Exceeded' column
        results_df = results_df.sort_values(by=f'Times Exceeded {threshold}%')
        
        st.subheader("Monthly Change Analysis for Each Stock")
        st.table(results_df.reset_index(drop=True))

        # Display stocks that never exceeded the threshold
        never_exceeded = results_df[results_df[f'Times Exceeded {threshold}%'] == 0]
        if not never_exceeded.empty:
            st.subheader(f"Stocks that never exceeded the {threshold}% threshold")
            st.table(never_exceeded[['Ticker', f'Times Exceeded {threshold}%']].reset_index(drop=True))
        else:
            st.subheader(f"All stocks exceeded the {threshold}% threshold at least once")
    else:
        st.error("No valid data available for any of the provided tickers.")