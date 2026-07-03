from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI(title="FinPulse API")

def get_db():
    conn = sqlite3.connect("finpulse.db")
    conn.row_factory = sqlite3.Row  # lets us return dict-like rows
    return conn

@app.get("/stocks")
def get_all_stocks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM stocks").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/stocks/{ticker}")
def get_stock(ticker: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM stocks WHERE ticker = ?", (ticker,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return dict(row)

@app.get("/market-summary")
def market_summary():
    conn = get_db()
    row = conn.execute("""
        SELECT COUNT(*) as total_stocks,
               AVG(pe_ratio) as avg_pe,
               MAX(market_cap) as largest_market_cap
        FROM stocks
    """).fetchone()
    conn.close()
    return dict(row)