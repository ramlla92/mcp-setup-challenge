#!/usr/bin/env python3
"""
Fetch historical stock data for selected tickers and perform basic EDA.

Follows instructions in .github/copilot-instructions.md: uses yfinance,
saves CSVs and PNG plots, prints previews and summary statistics.

Run: python scripts/fetch_and_eda.py
"""
import os
from datetime import datetime
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns


# -------------------------
# User configuration
# -------------------------
# Stocks and date range requested by the user
TICKERS = ["AAPL", "TSLA", "MSFT"]
START_DATE = "2023-01-01"
END_DATE = "2024-01-31"

# Directories for outputs
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "plots")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)


def fetch_ticker(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download data for a single ticker and return a DataFrame.

    The function ensures the index is a DatetimeIndex and returns the
    yfinance DataFrame directly so it can be saved and analyzed.
    """
    df = yf.download(ticker, start=start, end=end, progress=False)
    df.index = pd.to_datetime(df.index)
    return df


def main():
    all_data = {}

    # Fetch data for each ticker and save raw CSVs
    for t in TICKERS:
        print(f"Downloading {t} {START_DATE} -> {END_DATE}...")
        df = fetch_ticker(t, START_DATE, END_DATE)
        if df.empty:
            print(f"Warning: no data downloaded for {t}")
        csv_path = os.path.join(DATA_DIR, f"{t}.csv")
        df.to_csv(csv_path)
        print(f"Saved raw CSV: {csv_path}")
        print(df.head(5))
        all_data[t] = df

    # Combine closing prices into a single DataFrame for comparison
    close_df = pd.DataFrame({t: all_data[t]["Close"] for t in TICKERS})

    # Summary statistics and missing values
    summary_stats = close_df.describe()
    missing_counts = close_df.isnull().sum()

    summary_stats_path = os.path.join(DATA_DIR, "summary_stats.csv")
    missing_path = os.path.join(DATA_DIR, "missing_values.csv")
    summary_stats.to_csv(summary_stats_path)
    missing_counts.to_csv(missing_path, header=["missing_count"]) 
    print("Summary statistics:\n", summary_stats)
    print("Missing values per ticker:\n", missing_counts)

    # Simple missing-value handling: forward-fill then back-fill remaining gaps
    cleaned_close = close_df.ffill().bfill()
    cleaned_path = os.path.join(DATA_DIR, "closing_prices_cleaned.csv")
    cleaned_close.to_csv(cleaned_path)
    print(f"Saved cleaned closing prices CSV: {cleaned_path}")

    # Plot each ticker's closing price trend
    sns.set(style="darkgrid")
    for t in TICKERS:
        plt.figure(figsize=(10, 4))
        plt.plot(all_data[t].index, all_data[t]["Close"], label=f"{t} Close")
        plt.title(f"{t} Closing Price ({START_DATE} to {END_DATE})")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.tight_layout()
        out_file = os.path.join(PLOTS_DIR, f"{t}_closing_price.png")
        plt.savefig(out_file)
        plt.close()
        print(f"Saved plot: {out_file}")

    # Combined closing price comparison plot
    plt.figure(figsize=(12, 6))
    for t in TICKERS:
        plt.plot(cleaned_close.index, cleaned_close[t], label=t)
    plt.title(f"Closing Price Comparison: {', '.join(TICKERS)}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    combined_out = os.path.join(PLOTS_DIR, "combined_closing_prices.png")
    plt.savefig(combined_out)
    plt.close()
    print(f"Saved combined plot: {combined_out}")


if __name__ == "__main__":
    main()
