# Validation rows

For automated or semi-automated data-gathering (e.g. using large language models), it's recommended to provide the CSV header row and several rows of data in order to ensure conformity with structure.

These can be taken from the data CSV (`company_data.csv`).

At a minimum, provide one header and one row. Preferably, provide the header row and three rows of data.

Here's an example of a row block:

```csv
company_name,stock_ticker,exchange,sector,sics_sector,ebitda_2022,ebitda_currency,ebitda_unit,non_usd,ebitda_source,sustainability_report,headquarters_country,iso_3166_code,scope_1_emissions,scope_2_emissions,scope_3_emissions,emissions_reporting_unit,notes
Syensqo,SYEN,Euronext,Materials,1513,1.86,EUR,billion,1,https://www.syensqo.com/sites/g/files/alwlxe161/files/2024-03/2023Q4_PR_EN_FINAL.pdf,https://www.syensqo.com/en/press-release/syensqo-full-year-2023-results,Belgium,BE,2.1,1.0,8.4,million tonnes CO₂e,
```