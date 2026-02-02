#!/usr/bin/env python3
"""
stock_eda.py

Main script to fetch historical stock data (yfinance), perform basic EDA,
plot closing price trends, and save cleaned data + plots.

Follows `.github/copilot-instructions.md` requirements: shows imports at
top, prints previews, summary stats, checks/handles missing values,
saves CSVs and PNGs, and includes explanatory comments.

Run from `mcp-setup-challenge` with:
    python stock_eda.py
"""

# Imports required at top (explicitly shown per instructions)
import os
import sys
from typing import List, Tuple
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------
# Configuration / defaults
# -----------------------
DEFAULT_TICKERS = ["AAPL", "TSLA", "MSFT"]
DEFAULT_START = "2023-01-01"
DEFAULT_END = "2024-01-31"

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
PLOTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "plots")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)


def prompt_user() -> Tuple[List[str], str, str]:
    """Ask which stocks and date range to fetch, with sane defaults.

    Per `.github/copilot-instructions.md` we start by asking the user this
    question. If the user presses Enter, defaults are used so the script
    can run non-interactively.
    """
    msg = (
        "Which stock(s) and date range should I fetch?\n"
        "Enter tickers (comma-separated), start date YYYY-MM-DD, end date YYYY-MM-DD\n"
        f"Press Enter to use defaults: {','.join(DEFAULT_TICKERS)};{DEFAULT_START};{DEFAULT_END}\n> "
    )
    # If the environment variable MCP_AUTOMATE is set, use defaults and skip prompt.
    if os.getenv("MCP_AUTOMATE"):
        return DEFAULT_TICKERS, DEFAULT_START, DEFAULT_END

    inp = input(msg).strip()
    if not inp:
        return DEFAULT_TICKERS, DEFAULT_START, DEFAULT_END
    # Parse input expecting either: tickers;start;end  or tickers only
    parts = [p.strip() for p in inp.split(";")]
    tickers = [t.strip().upper() for t in parts[0].split(",") if t.strip()]
    start = parts[1] if len(parts) > 1 and parts[1] else DEFAULT_START
    end = parts[2] if len(parts) > 2 and parts[2] else DEFAULT_END
    if not tickers:
        tickers = DEFAULT_TICKERS
    return tickers, start, end


def fetch_data(tickers: List[str], start: str, end: str) -> dict:
    """Fetch historical OHLCV data for each ticker and return a dict of DataFrames.

    Uses `yfinance.download` to get price data. Ensures the index is DatetimeIndex.
    """
    out = {}
    for t in tickers:
        print(f"Downloading {t} from {start} to {end}...")
        df = yf.download(t, start=start, end=end, progress=False)
        df.index = pd.to_datetime(df.index)
        print(f"Preview for {t} (first 5 rows):")
        print(df.head(5))
        out[t] = df
        # Save raw individual CSV
        raw_path = os.path.join(DATA_DIR, f"{t}_raw.csv")
        df.to_csv(raw_path)
        print(f"Saved raw CSV: {raw_path}")
    return out


def perform_eda(data: dict):
    """Perform EDA: summary stats, missing value checks, simple cleaning.

    - Combine close prices for summary stats and missing-value overview.
    - Clean with forward-fill then back-fill and save cleaned CSVs.
    """
    # Build combined closing-price DataFrame.
    # Fixes implemented here:
    # - For a single stock, create a DataFrame from its Close Series (preserving Date index).
    # - For multiple stocks, concatenate each ticker's Close Series into a DataFrame
    #   with tickers as columns and Date as the index.
    # This avoids the ValueError raised when pandas is given scalar values.
    close_series = {}
    for t, df in data.items():
        # Preferred: explicit 'Close' column
        if "Close" in df.columns:
            s = df["Close"]
            # If yfinance returns a DataFrame slice, reduce to Series
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            close_series[t] = s
            continue

        # If columns are MultiIndex or named differently, look for any column name
        # that contains 'close' (case-insensitive) and use it.
        found = False
        cols = getattr(df, "columns", None)
        if cols is not None:
            for col in cols:
                if "close" in str(col).lower():
                    s = df[col]
                    if isinstance(s, pd.DataFrame):
                        s = s.iloc[:, 0]
                    close_series[t] = s
                    found = True
                    break

        if not found:
            # Fallback: use the first numeric column available (likely Close or Adj Close)
            numeric = df.select_dtypes(include=["number"]) if hasattr(df, "select_dtypes") else None
            if numeric is not None and not numeric.empty:
                close_series[t] = numeric.iloc[:, 0]
            else:
                # If nothing usable, create an empty Series with the same index
                close_series[t] = pd.Series(index=df.index, dtype="float64")

    # If only one ticker, turn the Series into a DataFrame with the Date index preserved.
    if len(close_series) == 1:
        only_ticker = next(iter(close_series))
        single_series = close_series[only_ticker]
        # Ensure it's a Series with a DatetimeIndex, then convert to DataFrame
        if isinstance(single_series, pd.Series):
            close_df = single_series.to_frame(name=only_ticker)
        else:
            close_df = pd.DataFrame({only_ticker: single_series})
    else:
        # For multiple tickers, concatenate along columns ensuring Date index alignment
        close_df = pd.concat(close_series, axis=1)

    # Summary statistics
    summary = close_df.describe()
    summary_path = os.path.join(DATA_DIR, "summary_stats.csv")
    summary.to_csv(summary_path)
    print("Summary statistics:\n", summary)
    print(f"Saved summary stats to {summary_path}")

    # Missing values
    missing = close_df.isnull().sum()
    missing_path = os.path.join(DATA_DIR, "missing_values.csv")
    missing.to_csv(missing_path, header=["missing_count"]) 
    print("Missing values per ticker:\n", missing)
    print(f"Saved missing-values report to {missing_path}")

    # Simple cleaning strategy: forward-fill then back-fill
    cleaned = close_df.ffill().bfill()
    cleaned_path = os.path.join(DATA_DIR, "closing_prices_cleaned.csv")
    cleaned.to_csv(cleaned_path)
    print(f"Saved cleaned closing prices to {cleaned_path}")
    return cleaned


def plot_prices(data: dict, cleaned_close: pd.DataFrame):
    """Plot each ticker's Close time series and a combined comparison plot.

    Saves PNG files to the `plots/` directory and prints saved locations. The
    copilot instructions suggest asking the user for preferred style; we use
    a clear line plot as the default.
    """
    sns.set(style="darkgrid")
    for t, df in data.items():
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df["Close"], label=f"{t} Close")
        plt.title(f"{t} Closing Price")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.tight_layout()
        out_file = os.path.join(PLOTS_DIR, f"{t}_closing_price.png")
        plt.savefig(out_file)
        plt.close()
        print(f"Saved plot: {out_file}")

    # Combined comparison
    plt.figure(figsize=(12, 6))
    for t in cleaned_close.columns:
        plt.plot(cleaned_close.index, cleaned_close[t], label=t)
    plt.title("Closing Price Comparison")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    combined = os.path.join(PLOTS_DIR, "combined_closing_prices.png")
    plt.savefig(combined)
    plt.close()
    print(f"Saved combined comparison plot: {combined}")


def save_cleaned_individuals(cleaned_close: pd.DataFrame, original_data: dict):
    """For each ticker, merge cleaned close values back into original and save CSVs.

    This preserves other columns in the original OHLCV data while replacing
    any missing Close values with cleaned values.
    """
    for t, orig in original_data.items():
        df_copy = orig.copy()
        if "Close" in df_copy.columns:
            df_copy["Close"] = cleaned_close[t]
        out_path = os.path.join(DATA_DIR, f"{t}_cleaned.csv")
        df_copy.to_csv(out_path)
        print(f"Saved cleaned CSV for {t}: {out_path}")


def main():
    # Ask the user (per instructions). Defaults used when input is empty.
    tickers, start, end = prompt_user()

    # Fetch data and keep in pandas DataFrames (requirement)
    data = fetch_data(tickers, start, end)

    if not data:
        print("No data fetched. Exiting.")
        sys.exit(1)

    # EDA: summary, missing value checks, simple cleaning
    cleaned_close = perform_eda(data)

    # Save cleaned individual DataFrames merging cleaned Close back to full OHLCV
    save_cleaned_individuals(cleaned_close, data)

    # Plot trends and save PNGs
    plot_prices(data, cleaned_close)

    print("Finished EDA. Data saved under 'data/' and plots under 'plots/'.")


if __name__ == "__main__":
    main()
