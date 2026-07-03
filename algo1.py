import yfinance as yf
import sqlite3
from datetime import datetime

# 20 well-known NSE stocks across sectors
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "NESTLEIND.NS", "BAJFINANCE.NS"
]

def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT,
            company_name TEXT,
            price REAL,
            market_cap REAL,
            pe_ratio REAL,
            eps REAL,
            fetched_at TEXT
        )
    """)
    conn.commit()

def fetch_and_store(conn):
    for symbol in TICKERS:
        try:
            info = yf.Ticker(symbol).info
            conn.execute("""
                INSERT INTO stocks (ticker, company_name, price, market_cap, pe_ratio, eps, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                info.get("longName"),
                info.get("currentPrice"),
                info.get("marketCap"),
                info.get("trailingPE"),
                info.get("trailingEps"),
                datetime.now().isoformat()
            ))
            print(f"✔ Stored {symbol}")
        except Exception as e:
            print(f"✘ Failed {symbol}: {e}")
    conn.commit()

if __name__ == "__main__":
    conn = sqlite3.connect("finpulse.db")
    create_table(conn)
    fetch_and_store(conn)
    conn.close()
    print("Done.")