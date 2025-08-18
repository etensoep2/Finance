import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Wall Street Bets")

stock1 = yf.Ticker("PLTR")
info1 = stock1.info
company_name1 = info.get("longName", "N/A")
current_price1 = info.get("currentPrice", "N/A")
pe_ratio1 = info.get("trailingPE", "N/A")

st.write(f"### {company_name} ({ticker})")
st.write(f"💰 Current Price: ${current_price}")
st.write(f"📊 P/E Ratio (Trailing): {pe_ratio}")

