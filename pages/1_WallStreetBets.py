import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Wall Street Bets")

# Ticker symbol
ticker_symbol = "PLTR"
ticker = yf.Ticker(ticker_symbol)

# Fetch data
company_name = ticker.info.get("longName")
current_price = ticker.history(period="1d")["Close"].iloc[-1]
pe_ratio = ticker.info.get("trailingPE")

# Display in Streamlit

st.header(f"{company_name} ({ticker_symbol})")

# Use columns for side-by-side display
col1, col2 = st.columns(2)
col1.metric(label="💰 Current Price", value=f"${current_price:.2f}")
col2.metric(label="📊 P/E Ratio (Trailing)", value=f"{pe_ratio if pe_ratio else 'N/A'}")

# Optional: Add a line chart for price history
st.line_chart(ticker.history(period="24mo")["Close"])
##############################################################################################
st.header("Short Position")

# Authenticate using the JSON key
url = "https://docs.google.com/spreadsheets/d/1pE7_z49F9TkKy4obgd63b1Ioo6V0ZmM0VhmZk78XQLY/export?format=csv"
df = pd.read_csv(url)

Profit = df.iloc[22, 1]
Value = df.iloc[12, 1]
margin = pd.to_numeric(Value, errors="coerce")/5

st.write("Current Position Value",Value)
st.write("Total Margin",margin)
st.write("Total Profit", Profit)

