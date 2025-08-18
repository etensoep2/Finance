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

raw_profit = df.iloc[15, 1]  # string from sheet
str_profit = str(raw_profit).replace(",", ".")  # swap comma with dot
Profit = pd.to_numeric(str_profit, errors="coerce")
raw_cost = df.iloc[11, 2]
str_cost = str(raw_cost).replace(",", ".")  # swap comma with dot
Cost = pd.to_numeric(str_cost, errors="coerce")
raw_value = df.iloc[12, 1]  # string from sheet
str_value = str(raw_value).replace(",", ".")  # swap comma with dot
Value = pd.to_numeric(str_value, errors="coerce")
margin = Value * 0.2
# Display in Streamlit

st.header(f"{company_name} ({ticker_symbol})")

# Use columns for side-by-side display
col1, col2 = st.columns(2)

col1, col2 = st.columns([1, 1])  # center it in col2
with col1:
    st.header("Short Position")
    st.metric("💰 Current Position Value", f"${Value:,.2f}")
    st.metric("💰 Cost Basis", f"${Cost:,.2f}")
    st.metric("📊 Total Margin", f"${margin:,.2f}")
    color = "green" if Profit > 0 else "red"
    st.markdown(f'<div style="font-size:28px;">📈 Profit: <span style="color:{"green" if Profit>0 else "red"}">${Profit:,.2f}</span></div>', unsafe_allow_html=True)
with col2:
    st.header("Stock Info")
    st.metric(label="💰 Current Price", value=f"${current_price:.2f}")
    st.metric(label="📊 P/E Ratio (Trailing)", value=f"{pe_ratio:.2f}" if pe_ratio else 'N/A')
    st.line_chart(ticker.history(period="24mo")["Close"],height=300)
# Optional: Add a line chart for price history
##############################################################################################
# Ticker symbol
ticker_symbol = "LIF"
ticker = yf.Ticker(ticker_symbol)

# Fetch data
company_name = ticker.info.get("longName")
current_price = ticker.history(period="1d")["Close"].iloc[-1]
pe_ratio = ticker.info.get("trailingPE")
market_cap = ticker.info.get("marketCap")

raw_profit = df.iloc[18, 3]  # string from sheet
str_profit = str(raw_profit).replace(",", ".")  # swap comma with dot
Profit = pd.to_numeric(str_profit, errors="coerce")
raw_cost = df.iloc[11, 4]
str_cost = str(raw_cost).replace(",", ".")  # swap comma with dot
Cost = pd.to_numeric(str_cost, errors="coerce")
raw_value = df.iloc[12, 3]  # string from sheet
str_value = str(raw_value).replace(",", ".")  # swap comma with dot
Value = pd.to_numeric(str_value, errors="coerce")
margin = Value * 0.2

st.header(f"{company_name} ({ticker_symbol})")

# Use columns for side-by-side display
col1, col2 = st.columns(2)

col1, col2 = st.columns([1, 1])  # center it in col2
with col1:
    st.header("Short Position")
    st.metric("💰 Current Position Value", f"${Value:,.2f}")
    st.metric("💰 Cost Basis", f"${Cost:,.2f}")
    st.metric("📊 Total Margin", f"${margin:,.2f}")
    color = "green" if Profit > 0 else "red"
    st.markdown(f'<div style="font-size:28px;">📈 Profit: <span style="color:{"green" if Profit>0 else "red"}">${Profit:,.2f}</span></div>', unsafe_allow_html=True)
with col2:
    st.header("Stock Info")
    st.metric(label="💰 Current Price", value=f"${current_price:.2f}")
    st.metric(label="📊 P/E Ratio (Trailing)", value=f"{pe_ratio:.2f}" if pe_ratio else 'N/A')
    st.line_chart(ticker.history(period="24mo")["Close"],height=300)
# Optional: Add a line chart for price history

