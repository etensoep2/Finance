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
st.line_chart(ticker.history(period="1mo")["Close"])
