import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Wall Street Bets")

stock1 = yf.Ticker("PLTR")
info1 = stock1.info
company_name1 = info1.get("longName", "N/A")
current_price1 = info1.get("currentPrice", "N/A")
pe_ratio1 = info1.get("trailingPE", "N/A")

st.write(f"### {company_name1} ({ticker})")
st.write(f"💰 Current Price: ${current_price1}")
st.write(f"📊 P/E Ratio (Trailing): {pe_ratio1}")

