import streamlit as st

def main_page():
    st.title("Stock Financial Projection")
    st.write("... your existing code ...")

def blog_page():
    st.title("📘 Blog Commentary")
    st.write("Write insights, thoughts, and commentary here.")
    st.text_area("Your notes:", height=200)

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Financial Projection", "Blog Commentary"])

if page == "Financial Projection":
    main_page()
elif page == "Blog Commentary":
    blog_page()
