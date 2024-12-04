# GHG Emissions Monetization Calculator

![View on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)(https://ghgemissionscalculator.streamlit.app/)

## Overview

The **GHG Emissions Monetization Calculator** is a Streamlit Cloud-deployed app designed to help users quantify and monetize greenhouse gas (GHG) emissions in relation to financial performance metrics. This tool is particularly useful for companies and analysts looking to integrate environmental impact data into financial analysis.

## Purpose

This app allows users to:
- Input GHG emissions data from companies (in tons of CO₂ equivalents).
- Match these emissions with the company's **EBITDA** (Earnings Before Interest, Taxes, Depreciation, and Amortization) for the previous financial year.
- Calculate the monetized cost of emissions using the **International Foundation for Valuing Impacts** proposed price of **$236 per ton of CO₂ equivalents**.
- Compute additional financial metrics, such as:
  - EBITDA minus total emissions cost.

## Features

- **Monetize Emissions:** The app multiplies GHG emissions data by $236 per ton to estimate the financial cost of environmental impact.
- **Financial Calculations:** Includes calculations for EBITDA and adjusted EBITDA (EBITDA minus total emissions cost).
- **CSV Export:** Generate a CSV row containing the calculated data, including a header row for easy aggregation and analysis across multiple datasets.
- **Streamlined Analysis:** Use the exported CSV data for further visualization or integration into your analysis workflows.

## How It Works

1. Input your company's GHG emissions data (in tons of CO₂ equivalents).
2. Enter the EBITDA figure from the previous financial year.
3. The calculator will:
   - Multiply emissions by $236/ton.
   - Display the monetized emissions cost.
   - Compute adjusted EBITDA values.
4. Click on **Generate CSV** to export your results for further use.

## Deployment

The app is hosted on Streamlit Cloud and can be accessed via this link:

[![View on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ghgemissionscalculator.streamlit.app/)

---

### Contributions

Contributions are welcome! Feel free to fork this repository, submit issues, or create pull requests to improve the functionality of this tool. 