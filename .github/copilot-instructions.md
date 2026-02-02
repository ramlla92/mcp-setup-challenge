# Copilot Agent Instructions

## General Behavior
- Write Python code step by step, clearly explaining each step in comments.
- Ask clarifying questions if instructions are vague.
- Avoid unnecessary code; keep it simple and readable.
- Always show imports required at the top of the script.

## Data Fetching
- Use `yfinance` to fetch stock data.
- Ensure the data is in a pandas DataFrame.
- Include date ranges when downloading stock data.
- Print a preview of the first 5 rows.

## Data Analysis / EDA
- Provide summary statistics (`describe()`).
- Check for missing values and handle them.
- Plot key trends (closing price, volume).
- Save plots as PNGs.
- Save the cleaned DataFrame as CSV.

## Documentation
- Include comments explaining why each step is done.
- Use markdown comments in code for clarity.

# Rule-Based Behavior
- Always start by asking: "Which stock(s) and date range should I fetch?"
- Always suggest saving CSV and PNGs after plots.
- Always confirm if plotting style should be lineplot or other types.
- Avoid executing risky operations (like deleting files).
