from algo1 import create_table, fetch_and_store
import sqlite3
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="FinPulse", layout="wide")
st.title("📊 FinPulse — Indian Stock Market Dashboard")
if st.button("🔄 Refresh Live Data"):
    conn = sqlite3.connect("finpulse.db")
    create_table(conn)
    fetch_and_store(conn)
    conn.close()
    st.success("Data refreshed!")
    st.rerun()

def load_data():
    conn = sqlite3.connect("finpulse.db")
    df = pd.read_sql_query("SELECT * FROM stocks", conn)
    conn.close()
    return df

df = load_data()

# --- Overview table ---
st.subheader("Market Overview")
st.dataframe(df[["ticker", "company_name", "price", "market_cap", "pe_ratio", "eps"]], use_container_width=True)

# --- Company selector + historical chart ---
st.subheader("Historical Price Chart")
selected_ticker = st.selectbox("Select a company", df["ticker"])

period = st.select_slider("Time period", options=["1mo", "3mo", "6mo", "1y", "5y"], value="6mo")
hist = yf.Ticker(selected_ticker).history(period=period)

fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name=selected_ticker))
fig.update_layout(xaxis_title="Date", yaxis_title="Price (₹)")
st.plotly_chart(fig, use_container_width=True)

# --- Company comparison ---
st.subheader("Compare Companies")
compare_tickers = st.multiselect("Select companies to compare", df["ticker"], default=df["ticker"][:3].tolist())

if compare_tickers:
    compare_fig = go.Figure()
    for t in compare_tickers:
        h = yf.Ticker(t).history(period=period)
        # Normalize to % change so different price scales are comparable
        normalized = (h["Close"] / h["Close"].iloc[0] - 1) * 100
        compare_fig.add_trace(go.Scatter(x=h.index, y=normalized, mode="lines", name=t))
    compare_fig.update_layout(xaxis_title="Date", yaxis_title="% Change", title="Normalized Price Comparison")
    st.plotly_chart(compare_fig, use_container_width=True)

# --- Fundamentals comparison ---
st.subheader("Fundamentals Comparison")
metric = st.radio("Metric", ["pe_ratio", "market_cap", "eps"], horizontal=True)
bar_fig = go.Figure(go.Bar(x=df["ticker"], y=df[metric]))
bar_fig.update_layout(yaxis_title=metric)
st.plotly_chart(bar_fig, use_container_width=True)