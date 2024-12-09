# GHG Emissions Monetization Calculator

[![View on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ghgemissionscalculator.streamlit.app/)

![alt text](screenshots/v1/1.png)

# Overview

What if companies had to foot the bill for the emissions that they caused? 

If that were the case, would airlines still be profitable? And how much would the profitability of oil and gas companies be degraded? 

This is an interesting question that gets to the heart of impact accounting and why many believe that it would be a fundamental improvement upon our current system of valuing business performance.

In order to facilitate an open-ended exploration of the interrelationship between profit and sustainability performance, two data points were chosen for analysis. 

- Firstly, greenhouse gas emissions (GHG), as these are widely reported by companies in the form of sustainability and ESG disclosures.
- To enable comparability between industries with often very different environmental footprints. These were standardized on millions of tons of carbon dioxide equivalents.
- Secondly, earnings before interest, tax depreciation and amortization (EBTIDA) was selected as the yardstick for profitability.

The EBITDA figure was calculated at year end in order to provide comparability between the sustainability reporting, which is typically reported retrospectively. Because 2023 reporting frequently reflects 2022 emissions, the financial metric was chosen for the same year.

The visualization tool deployed on Streamlit is backed by data, which is included in this repository at the root level (see: `company_data.csv`). Additionally, the companies included are tagged with their stock ticker (for a future visualisation including live financial feeds). The country in which they are headquartered is included both in its common descriptor and its ISO-3166 identifier.

Although currently not implemented for visualization, these could also be analyzed to attempt to understand the differences in emissions performance between countries and industries.

Gathering and verifying emissions data is a lengthy process. Contributions to the source data and corrections are more than welcome. If you have either, please open a pull request editing the CSV and not other parts of the repository.

# Methodology Notes

## Monetisation

To "monetise" greenhouse gas emissions (represent them in financial terms), the $236/TCO2E number proposed by the [International Foundation for Valuing Impacts](https://www.ifvi.org) was used.

## Units

For a detailed explanation, see "reporting units" (under notes).

**GHG emissions:** millions of tonnes of carbon dioxide equivalents.  
**Earnings before interest tax, depreciation, and amortization (EBITDA):** billions of US dollars.

## Data Sources

- Companies' ESG and sustainability disclosures for 2023 (retrieved from search engines)  
- Companies' EBITDA estimate for year end 2022

### GHG Emissions: MTCO2E

As noted in the reporting units document, GHG emissions were standardised on millions of (metric) tonnes of carbon dioxide equivalents (MTCO2E is frequently also denoted MMT20CE to make the 'metric' tonne clear). While the accurate scientific notation requests a subscript 'e,' to ensure a straightforward character set for data processing, it was denoted as it appears here, instead.

### EBITDA

Note: it is commonplace to encounter various differences in EBITDA, especially when it is calculated by financial analysts in addition to companies (and especially when various analysts compute different values for it). 

Unlike "operating income" (EBIT), EBITDA is a non-GAAP financial metric and thus, for American reporters, does not have to be included in SEC filings. Where multiple estimates at EBITDA were encountered, and when none of them were primary sources (ie, released by the company), an attempt was made to chose the most credible source.

---

## Screenshots, V2

![alt text](screenshots/v1/1.png)

![alt text](screenshots/v1/2.png)

![alt text](screenshots/v1/3.png)

![alt text](screenshots/v1/4.png)

![alt text](screenshots/v1/5.png)

![alt text](screenshots/v1/6.png)

![alt text](screenshots/v1/7.png)