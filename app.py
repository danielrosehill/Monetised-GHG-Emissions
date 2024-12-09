import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Load the CSV file dynamically
@st.cache_data
def load_data():
    return pd.read_csv('https://raw.githubusercontent.com/danielrosehill/GHG-Emissions-Data-Pipeline/refs/heads/main/company_data.csv')

# Function to format financial values
def format_financial(value):
    return f"${value:.2f}B"

# Function to format emissions values
def format_emissions(value):
    return f"{int(value):,}"

# Load data
data = load_data()

# Title and purpose
st.title('Monetized GHG Emissions Explorer')
st.write('This tool explores public sustainability disclosures and their financial implications, comparing 2023 emissions data against 2022 EBITDA figures.')

badge_markdown = """
[![View Repository](https://img.shields.io/badge/GitHub-View%20Repository-blue)](https://github.com/danielrosehill/Monetised-GHG-Emissions)
"""
st.sidebar.markdown(badge_markdown, unsafe_allow_html=True)

# Add correlation analysis
st.sidebar.divider()
with st.sidebar.expander("Dataset Correlation Estimate"):
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

# Sector Analysis
st.sidebar.divider()
with st.sidebar.expander("Sector Analysis"):
    sector_metrics = data.groupby('sector').agg({
        'total_emissions': 'mean',
        'emissions_per_billion_ebitda': 'mean'
    }).round(0)
    
    selected_sector = st.selectbox('Select Sector', data['sector'].unique())
    sector_avg_emissions = sector_metrics.loc[selected_sector, 'total_emissions']
    sector_avg_intensity = sector_metrics.loc[selected_sector, 'emissions_per_billion_ebitda']
    
    st.metric("Sector Average Emissions (MT CO₂e)", format_emissions(sector_avg_emissions))
    st.metric("Sector Average Intensity", format_emissions(sector_avg_intensity))

# Sidebar for selecting companies
st.sidebar.title('Select Companies')
selected_companies = st.sidebar.multiselect(
    'Choose companies to compare',
    data['company_name'].unique(),
    max_selections=5
)

# Filter data for selected companies
filtered_data = data[data['company_name'].isin(selected_companies)]

if not filtered_data.empty:
    filtered_data['total_emissions'] = (filtered_data['scope_1_emissions'] + 
                                      filtered_data['scope_2_emissions'] + 
                                      filtered_data['scope_3_emissions'])
    filtered_data['total_emissions_formatted'] = filtered_data['total_emissions'].apply(format_emissions)
    filtered_data['monetized_all_scope_emissions'] = filtered_data['total_emissions'] * 236_000_000 / 1_000_000_000
    filtered_data['ebitda_minus_monetized_emissions'] = filtered_data['ebitda_2022'] - filtered_data['monetized_all_scope_emissions']

    # Calculate scope percentages
    filtered_data['scope1_pct'] = (filtered_data['scope_1_emissions'] / filtered_data['total_emissions']) * 100
    filtered_data['scope2_pct'] = (filtered_data['scope_2_emissions'] / filtered_data['total_emissions']) * 100
    filtered_data['scope3_pct'] = (filtered_data['scope_3_emissions'] / filtered_data['total_emissions']) * 100

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Emissions Analysis", "Financial Impact", "Geographic Analysis", "Sector Comparison"])

with tab1:
    if not filtered_data.empty:
        st.subheader('Emissions Breakdown by Scope')
        
        # Stacked bar chart
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
        
        # Emissions table
        st.subheader('Detailed Emissions Data')
        emissions_table = filtered_data[['company_name', 'scope_1_emissions', 'scope_2_emissions', 
                                       'scope_3_emissions', 'total_emissions']]
        emissions_table = emissions_table.round(0)
        emissions_table.columns = ['Company', 'Scope 1', 'Scope 2', 'Scope 3', 'Total Emissions']
        st.table(emissions_table.applymap(lambda x: format_emissions(x) if isinstance(x, (int, float)) else x))

with tab2:
    if not filtered_data.empty:
        st.subheader('EBITDA minus Emissions')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(filtered_data))
        width = 0.25
        
        # Three bars per company
        bars1 = ax.bar(x - width, filtered_data['ebitda_2022'], width, label='EBITDA', color='blue')
        bars2 = ax.bar(x, -filtered_data['monetized_all_scope_emissions'], width, label='Monetized Emissions', color='red')
        bars3 = ax.bar(x + width, filtered_data['ebitda_minus_monetized_emissions'], width, 
                      label='Net EBITDA', color='green')
        
        # Add value labels
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${abs(height):.2f}B',
                       ha='center', va='bottom')
        
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)
        
        plt.xlabel('Company')
        plt.ylabel('Billion $')
        plt.title('EBITDA minus Emissions Analysis')
        plt.xticks(x, filtered_data['company_name'], rotation=45)
        plt.legend()
        
        st.pyplot(fig)
        
        # Financial metrics table
        st.subheader('Financial Metrics')
        financial_table = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 
                                       'ebitda_minus_monetized_emissions']]
        financial_table.columns = ['Company', 'EBITDA', 'Monetized Emissions', 'Net EBITDA']
        
        # Format financial columns
        for col in ['EBITDA', 'Monetized Emissions', 'Net EBITDA']:
            financial_table[col] = financial_table[col].apply(format_financial)
            
        st.table(financial_table)

with tab3:
    if not filtered_data.empty:
        st.subheader('Geographic Distribution')
        
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
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=filtered_data, x='ebitda_2022', y='emissions_per_billion_ebitda', 
                       hue='sector', style='sector', s=100)
        plt.xlabel('EBITDA (Billion $)')
        plt.ylabel('Emissions Intensity (MT CO₂e/B$)')
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Source data display
st.subheader('Source Data')
if not filtered_data.empty:
    source_data = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 'total_emissions']]
    source_data.columns = ['Company Name', 'EBITDA', 'Monetized Emissions', 'Total Emissions']
    
    # Format financial columns
    source_data['EBITDA'] = source_data['EBITDA'].apply(format_financial)
    source_data['Monetized Emissions'] = source_data['Monetized Emissions'].apply(format_financial)
    source_data['Total Emissions'] = source_data['Total Emissions'].apply(format_emissions)
    
    st.dataframe(source_data)
else:
    st.write('Please select companies from the sidebar to view the source data.')

# App information
with st.sidebar.expander("About This App"):
    st.write("Emissions are monetized at the rate of $236 per ton of carbon dioxide equivalents as proposed by the International Foundation for Valuing Impacts.")

# Credits
with st.sidebar.expander("Credits"):
    st.write("This app was developed by Daniel Rosehill.")