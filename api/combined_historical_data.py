import pandas as pd
import datetime as dt
import yfinance as yf, glob

# 🗓️ Time range
start = dt.date.today() - dt.timedelta(days=10*365)
end   = dt.date.today()

# US tickers
us_symbols = us_symbols = [
    "AAPL","ABBV","ABT","ACN","ADBE","AIG","AMD","AMGN","AMT","AMZN",
    "AVGO","AXP","BA","BAC","BK","BKNG","BLK","BMY","BRK.B","C",
    "CAT","CHTR","CL","CMCSA","COF","COP","COST","CRM","CSCO","CVS",
    "CVX","DE","DHR","DIS","DUK","EMR","FDX","GD","GE","GILD",
    "GM","GOOG","GOOGL","GS","HD","HON","IBM","INTC","INTU","ISRG",
    "JNJ","JPM","KO","LIN","LLY","LMT","LOW","MA","MCD","MDLZ",
    "MDT","MET","META","MMM","MO","MRK","MS","MSFT","NEE","NFLX",
    "NKE","NOW","NVDA","ORCL","PEP","PFE","PG","PLTR","PM","PYPL",
    "QCOM","RTX","SBUX","SCHW","SO","SPG","T","TGT","TMO","TMUS",
    "TSLA","TXN","UNH","UNP","UPS","USB","V","VZ","WFC","WMT",
    "XOM",
]

dfs = []

for sym in us_symbols:
    try:
        df = yf.download(sym, start=start, end=end)
        df['Symbol'] = sym
        dfs.append(df.reset_index())
    except Exception as e:
        print(f"Error fetching {sym}: {e}")

# 2️⃣ UAE ETF 
uae_df = pd.read_csv("UAE_stock_data.csv", parse_dates=['Date'])
uae_df['Symbol'] = 'UAE_ISHARES'
uae_df = uae_df.rename(columns={'Close':'Adj Close'})
dfs.append(uae_df)

# 3️⃣ DFM data (up to 2 years)
for f in glob.glob("DFM_*.csv"):
    df = pd.read_csv(f, parse_dates=['Date'])
    df['Symbol'] = f.split("_")[1].split(".")[0]
    df = df.rename(columns={'Close':'Adj Close'})
    dfs.append(df)

# 4️⃣ Nasdaq Dubai data
for f in glob.glob("NasdaqDubai_*.csv"):
    df = pd.read_csv(f, parse_dates=['Date'])
    df['Symbol'] = f.split("_")[1].split(".")[0]
    df = df.rename(columns={'Close':'Adj Close'})
    dfs.append(df)

# Combine
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('combined_historical.csv', index=False)
print("✅ Saved combined_historical.csv")
