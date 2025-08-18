import streamlit as st

st.title("📘 Blog Commentary")

st.write("""
Welcome to the commentary section!  
Here you can write analysis, insights, or market notes in a blog-style format.
""")

st.header("Market Thoughts")
st.write("Example: *Tech stocks are showing resilience despite market volatility.*")

st.header("Personal Notes")
st.text_area("Write your own notes here:", height=200)
