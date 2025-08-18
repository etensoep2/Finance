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
market_cap = ticker.info.get("marketCap")

# Authenticate using the JSON key
url = "https://docs.google.com/spreadsheets/d/1pE7_z49F9TkKy4obgd63b1Ioo6V0ZmM0VhmZk78XQLY/export?format=csv"
df = pd.read_csv(url)

Profit = df.iloc[22, 1]
Value = df.iloc[12, 1]
Cost = df.iloc[11, 2]
raw_value = df.iloc[12, 1]  # string from sheet
clean_value = str(raw_value).replace(",", ".")  # swap comma with dot
margin = pd.to_numeric(clean_value, errors="coerce") * 0.2
# Display in Streamlit

st.header(f"{company_name} ({ticker_symbol})")

# Use columns for side-by-side display
col1, col2 = st.columns(2)

col1, col2 = st.columns([1, 1])  # center it in col2
with col1:
    st.header("Short Position")
    st.metric("💰 Current Position Value", Value)
    st.metric("💰 Cost Basis", Cost)
    st.metric("📊 Total Margin", f"${margin:,.2f}")
    st.metric("📈 Total Profit", Profit)
with col2:
    st.metric(label="💰 Market Cap", value=f"${market_cap:.2f}")
    st.metric(label="💰 Current Price", value=f"${current_price:.2f}")
    st.metric(label="📊 P/E Ratio (Trailing)", value=f"{pe_ratio if pe_ratio else 'N/A'}")
    st.line_chart(ticker.history(period="24mo")["Close"],height=300)
# Optional: Add a line chart for price history
##############################################################################################
