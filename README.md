# MCP Setup Challenge

## Overview

This repository contains my MCP Setup Challenge project for 10 Academy. The goal of this challenge is to demonstrate foundational skills in configuring a coding environment with MCP tools, using AI agent assistants, and performing a simple data analysis workflow.

In this project, I worked on fetching historical stock data, performing basic exploratory data analysis (EDA), and saving the results, all under a local Python environment.

---

## Project Structure

│
├─ stock_eda.py # Main Python script for fetching and analyzing stock data 
├─ venv/ # Python virtual environment
├─ data/ # Folder where CSV files of stock data are saved
├─ plots/ # Folder where plots are saved
├─ .github/
│ └─ copilot-instructions.md # Instructions for AI assistant (Copilot)
├─ .gitignore # To ignore virtual environment, data, and plots
└─ README.md


---

## Workflow

1. **Set up Python virtual environment** in the project folder:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
Fetch stock data for AAPL, TSLA, MSFT from Jan 2023 to Jan 2024 using yfinance.

Perform basic EDA:

Summary statistics

Check for missing values

Plot closing price trends

---

## Save outputs:

CSV files for each stock in data/

Plots in plots/

Follow instructions in .github/copilot-instructions.md to guide Copilot while writing the script.

Git tracking: .gitignore includes venv/, data/, plots/ to avoid committing large files.

## Issues Encountered

### MCP Authentication Issue

While trying to connect VS Code to the Tenx MCP server, I received the following error:

```
{"error":"invalid_request","error_description":"Client ID '507712cc-426e-4b79-a8c5-a91ce8085ad1' not found","state":"..."}

```
This was a server-side issue with MCP authentication.

I was unable to fully connect the MCP server, so I focused on local Python and Copilot workflows for the challenge.
---
Results

Raw stock CSVs saved under data/

Closing price trend plots saved under plots/

Script runs successfully after fixing Pandas and path issues

Copilot instructions used to guide AI assistance during development
