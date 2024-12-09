import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Load the CSV file dynamically
@st.cache_data
def load_data():
    return pd.read_csv('company_data.csv')

# Function to calculate monetized emissions intensity ratio
def calculate_monetized_emissions_intensity_ratio(row):
    total_emissions = (row['scope_1_emissions'] + row['scope_2_emissions'] + row['scope_3_emissions']) * 236_000_000
    monetized_emissions_intensity = total_emissions / 1_000_000_000  # Convert to billions
    monetized_emissions_intensity_ratio = monetized_emissions_intensity / row['ebitda_2022']
    return monetized_emissions_intensity_ratio

# Load data
data = load_data()

# Title and purpose
st.title('Monetized GHG Emissions Explorer')
st.write('This tool explores public sustainability disclosures and their financial implications, comparing 2023 emissions data against 2022 EBITDA figures.')

# Add correlation analysis
st.sidebar.divider()
with st.sidebar.expander("Sustainability Performance vs Profitability"):
    data['total_emissions'] = (data['scope_1_emissions'] + 
                             data['scope_2_emissions'] + 
                             data['scope_3_emissions'])
    
    data['emissions_per_billion_ebitda'] = data['total_emissions'] / data['ebitda_2022']
    correlation = -1 * data['emissions_per_billion_ebitda'].corr(data['ebitda_2022'])
    
    st.metric(
        label="Correlation Coefficient",
        value=f"{correlation:.3f}",
        help="A positive value suggests companies with better sustainability performance tend to have higher profits."
    )

# New: Sector Analysis
st.sidebar.divider()
with st.sidebar.expander("Sector Analysis"):
    sector_metrics = data.groupby('sector').agg({
        'total_emissions': 'mean',
        'emissions_per_billion_ebitda': 'mean'
    }).round(2)
    
    selected_sector = st.selectbox('Select Sector', data['sector'].unique())
    sector_avg_emissions = sector_metrics.loc[selected_sector, 'total_emissions']
    sector_avg_intensity = sector_metrics.loc[selected_sector, 'emissions_per_billion_ebitda']
    
    st.metric("Sector Average Emissions (MT CO₂e)", f"{sector_avg_emissions:,.1f}")
    st.metric("Sector Average Intensity", f"{sector_avg_intensity:,.1f}")

# Sidebar for selecting companies
st.sidebar.title('Select Companies')
selected_companies = st.sidebar.multiselect(
    'Choose companies to compare',
    data['company_name'].unique(),
    max_selections=5
)

# Filter data for selected companies
filtered_data = data[data['company_name'].isin(selected_companies)]

# Calculate metrics for selected companies
if not filtered_data.empty:
    filtered_data['monetized_emissions_intensity_ratio'] = filtered_data.apply(calculate_monetized_emissions_intensity_ratio, axis=1)
    filtered_data['total_emissions'] = (filtered_data['scope_1_emissions'] + filtered_data['scope_2_emissions'] + filtered_data['scope_3_emissions'])
    filtered_data['total_emissions_formatted'] = filtered_data['total_emissions'].apply(lambda x: f"{x:,.2f} MTCO2E")
    filtered_data['monetized_all_scope_emissions'] = filtered_data['total_emissions'] * 236_000_000 / 1_000_000_000
    filtered_data['ebitda_minus_monetized_emissions'] = filtered_data['ebitda_2022'] - filtered_data['monetized_all_scope_emissions']

    # New: Calculate scope percentages
    filtered_data['scope1_pct'] = (filtered_data['scope_1_emissions'] / filtered_data['total_emissions']) * 100
    filtered_data['scope2_pct'] = (filtered_data['scope_2_emissions'] / filtered_data['total_emissions']) * 100
    filtered_data['scope3_pct'] = (filtered_data['scope_3_emissions'] / filtered_data['total_emissions']) * 100

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Emissions Analysis", "Financial Impact", "Geographic Analysis", "Sector Comparison"])

with tab1:
    if not filtered_data.empty:
        # Emissions Breakdown
        st.subheader('Emissions Breakdown by Scope')
        
        # Stacked bar chart for scope percentages
        fig, ax = plt.subplots(figsize=(10, 6))
        bottom_scope1 = np.zeros(len(filtered_data))
        bottom_scope2 = filtered_data['scope1_pct']
        bottom_scope3 = filtered_data['scope1_pct'] + filtered_data['scope2_pct']
        
        plt.bar(filtered_data['company_name'], filtered_data['scope1_pct'], label='Scope 1')
        plt.bar(filtered_data['company_name'], filtered_data['scope2_pct'], bottom=bottom_scope1, label='Scope 2')
        plt.bar(filtered_data['company_name'], filtered_data['scope3_pct'], bottom=bottom_scope2, label='Scope 3')
        
        plt.xlabel('Company')
        plt.ylabel('Percentage of Total Emissions')
        plt.title('Emissions Breakdown by Scope (%)')
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(fig)
        
        # Detailed emissions table
        st.subheader('Detailed Emissions Data')
        emissions_table = filtered_data[['company_name', 'scope_1_emissions', 'scope_2_emissions', 
                                       'scope_3_emissions', 'total_emissions_formatted']]
        emissions_table.columns = ['Company', 'Scope 1', 'Scope 2', 'Scope 3', 'Total Emissions']
        st.table(emissions_table)

with tab2:
    if not filtered_data.empty:
        st.subheader('Financial Impact Analysis')
        
        # Waterfall chart showing EBITDA impact
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(filtered_data))
        width = 0.35
        
        plt.bar(x, filtered_data['ebitda_2022'], width, label='Original EBITDA')
        plt.bar(x, -filtered_data['monetized_all_scope_emissions'], width, 
                bottom=filtered_data['ebitda_2022'], label='Carbon Cost')
        
        plt.xlabel('Company')
        plt.ylabel('Billion $')
        plt.title('EBITDA Impact of Monetized Emissions')
        plt.xticks(x, filtered_data['company_name'], rotation=45)
        plt.legend()
        
        st.pyplot(fig)
        
        # Financial metrics table
        st.subheader('Financial Metrics')
        financial_table = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 
                                       'ebitda_minus_monetized_emissions']]
        financial_table.columns = ['Company', 'EBITDA', 'Carbon Cost', 'Adjusted EBITDA']
        st.table(financial_table)

with tab3:
    if not filtered_data.empty:
        st.subheader('Geographic Distribution')
        
        # Group by country
        country_emissions = filtered_data.groupby('headquarters_country').agg({
            'total_emissions': 'sum',
            'company_name': 'count'
        }).reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=country_emissions, x='headquarters_country', y='total_emissions')
        plt.xlabel('Country')
        plt.ylabel('Total Emissions (MT CO₂e)')
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tab4:
    if not filtered_data.empty:
        st.subheader('Sector Comparison')
        
        # Emissions intensity by sector
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=filtered_data, x='ebitda_2022', y='emissions_per_billion_ebitda', 
                       hue='sector', style='sector', s=100)
        plt.xlabel('EBITDA (Billion $)')
        plt.ylabel('Emissions Intensity (MT CO₂e/B$)')
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Expander for app information
with st.sidebar.expander("About This App"):
    st.write("Emissions are monetized at the rate of $236 per ton of carbon dioxide equivalents as proposed by the International Foundation for Valuing Impacts.")

# Expander for credits
with st.sidebar.expander("Credits"):
    st.write("This app was developed by Daniel Rosehill.")

# Source data display
st.subheader('Source Data')
if not filtered_data.empty:
    source_data = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 'total_emissions_formatted']]
    source_data.columns = ['Company Name', 'EBITDA', 'Monetized All Scope Emissions', 'Total Emissions']
    source_data['EBITDA'] = source_data['EBITDA'].apply(lambda x: f"${x:.2f}B")
    source_data['Monetized All Scope Emissions'] = source_data['Monetized All Scope Emissions'].apply(lambda x: f"${x:.2f}B")
    st.dataframe(source_data)
else:
    st.write('Please select companies from the sidebar to view the source data.')