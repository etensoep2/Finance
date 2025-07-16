import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def get_financials(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    try:
        revenue = financials['Total Revenue'].dropna() / 1e9
        net_income = financials['Net Income'].dropna() / 1e9
        return revenue, net_income, stock
    except KeyError:
        st.warning(f"Missing 'Total Revenue' or 'Net Income' for {ticker}.")
        return pd.Series(), pd.Series(), None

def project_growth(values, growth_rate, years=4):
    if len(values) == 0:
        return []
    last = values[-1]
    projections = []
    for _ in range(years):
        last *= (1 + growth_rate)
        projections.append(last)
    return projections

# Streamlit UI
st.title("Stock Financials & Price Projection")

ticker = st.text_input("Enter Stock Ticker", value="AAPL")
rev_growth = st.slider("Revenue Growth Rate (%)", 0.0, 100.0, 8.0) / 100
ni_growth = st.slider("Net Income Growth Rate (%)", 0.0, 100.0, 8.0) / 100
pe_low = st.slider("Low P/E Estimate", 1.0, 800.0, 10.0)
pe_high = st.slider("High P/E Estimate", 1.0, 800.0, 25.0)

if ticker:
    revenue, net_income, stock = get_financials(ticker.upper())
    if stock:
        # You would continue adapting the logic from your `update_chart` function here
        # Plot revenue and net income similar to your matplotlib logic

        fig, ax = plt.subplots()
        ax.plot(revenue.index, revenue.values, label="Revenue")
        ax.plot(net_income.index, net_income.values, label="Net Income")
        ax.set_title(f"{ticker} Financials")
        ax.set_ylabel("Billions USD")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)