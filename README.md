# FinPulse

Stock market monitoring platform for SoFI's AlgoLabs Core Induction (Assignment 1). Tracks 20 NSE-listed companies, stores their market data, and shows it on a dashboard.

**Dashboard:** https://finpulse-27phmb7xrifs4vg9xfnrge.streamlit.app/
**API:** https://finpulse-api-yjel.onrender.com
**API docs:** https://finpulse-api-yjel.onrender.com/docs

The API is on Render's free tier, so it spins down when idle. First request after a while might take 30-60 seconds to wake up.

## How it's put together

Three separate pieces:

- **`algo1.py`** — fetches data for the 20 stocks using yfinance and writes it into `finpulse.db` (SQLite). Uses `INSERT ... ON CONFLICT DO UPDATE` so running it again updates the existing rows instead of piling up duplicates.
- **`api.py`** — FastAPI app that reads from the same database and serves it over REST. Deployed on Render.
- **`dashboard.py`** — Streamlit app, also reads directly from the database, renders tables and charts. Deployed on Streamlit Community Cloud.

API and dashboard are deployed separately with their own dependency files (`requirements-api.txt` for the API, `requirements.txt` for the dashboard). I split these after the API build kept failing on Render trying to compile `pyarrow`, which turned out to be a Streamlit/Plotly dependency the API doesn't even need.

## Stack

| Layer | Tech |
|---|---|
| Data | yfinance |
| Database | SQLite |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| API host | Render |
| Dashboard host | Streamlit Community Cloud |

## API endpoints

- `GET /stocks` — all 20 companies with price, market cap, P/E, EPS
- `GET /stocks/{ticker}` — one company by ticker (e.g. `/stocks/RELIANCE.NS`), 404 if not found
- `GET /market-summary` — total stocks tracked, average P/E, largest market cap, computed with SQL aggregation

`/docs` gets you Swagger UI for free through FastAPI, useful for testing endpoints without writing a separate client.

## Database

One table, `stocks`:

`ticker` (primary key), `company_name`, `price`, `market_cap`, `pe_ratio`, `eps`, `fetched_at`.

`ticker` being the primary key is what makes the upsert work — re-fetching updates rows instead of adding new ones each time.

## What's built

MVP stuff: live data for 20 companies across different sectors (banks, IT, FMCG, auto, pharma, cement), SQLite storage, 3 API endpoints, dashboard with a sortable table, historical price chart with adjustable time range, multi-company comparison chart, and a bar chart comparing fundamentals.

Extra stuff I added: a toggle between line and candlestick charts (uses OHLC data yfinance already gives you, just wasn't using it before), a refresh button on the dashboard that re-runs the same fetch logic from `algo1.py` instead of duplicating it, and the API/dashboard being deployed as fully independent services.

## Running it locally

```bash
git clone https://github.com/armaannbhansali/finpulse.git
cd finpulse

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python3 algo1.py

uvicorn api:app --reload
# separate terminal:
streamlit run dashboard.py
```

## What was hard

Honestly the environment/deployment side and the actual concepts (APIs, databases, SQL) were about equally difficult, since this was my first time building something like this end to end. Getting comfortable with the terminal vs. editor distinction, activating venvs consistently, and not confusing "run this as a command" vs "save this as a file" took a while to click.

The deployment failure was its own thing — `pip freeze` had dumped my entire local environment into `requirements.txt`, including packages the API never touches, and Render's build kept dying trying to compile one of them (`pyarrow`). Splitting into two separate requirements files fixed it, and also just made more sense architecturally once I thought about it — no reason the API build should care about Streamlit at all.

## What I'd add next

- Store historical prices in the DB instead of hitting yfinance live every time someone picks a date range
- Auto-refresh on a schedule instead of a manual button
- Login + personal watchlists
- More fundamentals than just P/E and EPS — debt/equity, ROE, that kind of thing

## AI use

Used Claude to walk through concepts I didn't know (venvs, REST APIs, SQL upserts, deployment), debug errors as they came up (the Render/pyarrow issue especially), and help structure this README. Wrote and tested all the code myself and can explain the actual decisions in it — the upsert logic, splitting the dependencies, normalizing prices to % change for the comparison chart, etc.
