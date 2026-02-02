# Stock EDA

This small utility fetches historical stock data for AAPL, TSLA, and MSFT (Jan 2023 → Jan 2024), performs basic EDA (summary statistics, missing values), plots closing-price trends, and saves CSVs and PNGs.

Run:

```bash
python scripts/fetch_and_eda.py
```

Outputs:
- `data/` : raw CSVs for each ticker and summary CSVs
- `plots/` : PNG plots for each ticker and a combined comparison plot
