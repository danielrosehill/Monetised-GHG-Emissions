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
st.write('The purpose of this tool is to allow users to explore data derived from public sustainability disclosures by publicly listed companies and comparing that data against their estimated earnings before interest tax depreciation and amortization. The financial metric is at year-end 2022 while the sustainability data is from 2023 reporting.')

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
        help="A positive value suggests companies with better sustainability performance tend to have higher profits. Values range from -1 to +1, where 0 indicates no correlation."
    )

# New Feature: Industry Benchmarking
if 'industry' in data.columns:
    with st.sidebar.expander("Industry Benchmarking"):
        selected_industry = st.selectbox(
            "Select Industry for Benchmarking",
            data['industry'].unique()
        )
        industry_avg_emissions = data[data['industry'] == selected_industry]['total_emissions'].mean()
        industry_avg_intensity = data[data['industry'] == selected_industry]['emissions_per_billion_ebitda'].mean()
        
        st.metric("Industry Average Emissions", f"{industry_avg_emissions:,.0f} MTCO2E")
        st.metric("Industry Average Intensity", f"{industry_avg_intensity:,.2f} MTCO2E/B$")

# Sidebar for selecting companies
st.sidebar.title('Select Companies')
selected_companies = st.sidebar.multiselect(
    'Choose up to 5 companies',
    data['company_name'].unique(),
    max_selections=5
)

# Filter data for selected companies
filtered_data = data[data['company_name'].isin(selected_companies)]

# Calculate additional metrics
if not filtered_data.empty:
    filtered_data['monetized_emissions_intensity_ratio'] = filtered_data.apply(calculate_monetized_emissions_intensity_ratio, axis=1)
    filtered_data['total_emissions'] = (filtered_data['scope_1_emissions'] + filtered_data['scope_2_emissions'] + filtered_data['scope_3_emissions'])
    filtered_data['total_emissions_formatted'] = filtered_data['total_emissions'].apply(lambda x: f"{x:.2f} MTCO2E")
    filtered_data['monetized_all_scope_emissions'] = filtered_data['total_emissions'] * 236_000_000 / 1_000_000_000
    filtered_data['ebitda_minus_monetized_emissions'] = filtered_data['ebitda_2022'] - filtered_data['monetized_all_scope_emissions']
    
    # New Feature: Year-over-Year Trend Analysis
    if 'emissions_2021' in filtered_data.columns:
        filtered_data['emissions_change'] = ((filtered_data['total_emissions'] - filtered_data['emissions_2021']) 
                                           / filtered_data['emissions_2021'] * 100)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Emissions Breakdown", "Financial Impact", "Trend Analysis", "Peer Comparison"])

# Tab 1: Emissions Breakdown by Scope
with tab1:
    st.subheader('Emissions Breakdown by Scope')
    if not filtered_data.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(filtered_data))
        width = 0.25
        
        ax.bar(x - width, filtered_data['scope_1_emissions'], width, label='Scope 1')
        ax.bar(x, filtered_data['scope_2_emissions'], width, label='Scope 2')
        ax.bar(x + width, filtered_data['scope_3_emissions'], width, label='Scope 3')
        
        ax.set_xticks(x)
        ax.set_xticklabels(filtered_data['company_name'], rotation=45)
        ax.legend()
        st.pyplot(fig)

# Tab 2: Financial Impact
with tab2:
    if not filtered_data.empty:
        st.subheader('Financial Impact of Monetized Emissions')
        impact_df = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 
                                 'ebitda_minus_monetized_emissions']]
        
        # Waterfall chart
        fig, ax = plt.subplots(figsize=(10, 6))
        for idx, company in enumerate(impact_df['company_name']):
            plt.bar(idx*3, impact_df.loc[impact_df['company_name']==company, 'ebitda_2022'],
                   label='Original EBITDA')
            plt.bar(idx*3+1, -impact_df.loc[impact_df['company_name']==company, 'monetized_all_scope_emissions'],
                   label='Monetized Emissions' if idx==0 else "")
            plt.bar(idx*3+2, impact_df.loc[impact_df['company_name']==company, 'ebitda_minus_monetized_emissions'],
                   label='Net EBITDA' if idx==0 else "")
        
        plt.xticks(np.arange(len(impact_df))*3+1, impact_df['company_name'], rotation=45)
        plt.legend()
        st.pyplot(fig)

# Tab 3: Trend Analysis
with tab3:
    if not filtered_data.empty and 'emissions_change' in filtered_data.columns:
        st.subheader('Year-over-Year Emissions Trend')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=filtered_data, x='company_name', y='emissions_change')
        plt.xticks(rotation=45)
        plt.ylabel('Emissions Change (%)')
        st.pyplot(fig)

# Tab 4: Peer Comparison
with tab4:
    if not filtered_data.empty:
        st.subheader('Peer Comparison')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=filtered_data, x='ebitda_2022', y='emissions_per_billion_ebitda')
        plt.xlabel('EBITDA (Billions $)')
        plt.ylabel('Emissions Intensity (MTCO2E/B$)')
        for idx, row in filtered_data.iterrows():
            plt.annotate(row['company_name'], (row['ebitda_2022'], row['emissions_per_billion_ebitda']))
        st.pyplot(fig)

# Expander for app information
with st.sidebar.expander("About This App"):
    st.write("Emissions are monetized at the rate of $236 per ton of carbon dioxide equivalents as proposed by the International Foundation for Valuing Impacts.")

# Expander for credits
with st.sidebar.expander("Credits"):
    st.write("This app was developed by Daniel Rosehill.")