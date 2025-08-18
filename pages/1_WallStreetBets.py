import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Wall Street Bets")

# Choose a stock ticker (e.g., Apple)
ticker_symbol = "PLTR"

# Create ticker object
ticker = yf.Ticker(ticker_symbol)

# Get stock price
price = ticker.history(period="1d")["Close"].iloc[-1]

# Get company name
company_name = ticker.info.get("longName")

# Get PE ratio (Trailing P/E)
pe_ratio = ticker.info.get("trailingPE")

st.write(f"### {company_name} ({ticker})")
st.write(f"💰 Current Price: ${current_price}")
st.write(f"📊 P/E Ratio (Trailing): {pe_ratio}")

