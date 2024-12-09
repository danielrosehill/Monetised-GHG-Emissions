import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

# Sidebar for selecting companies
st.sidebar.title('Select Companies')
selected_companies = st.sidebar.multiselect(
    'Choose up to 5 companies',
    data['company_name'].unique(),
    max_selections=5
)

# Expander for app information
with st.sidebar.expander("About This App"):
    st.write("Emissions are monetized at the rate of $236 per ton of carbon dioxide equivalents as proposed by the International Foundation for Valuing Impacts.")

# Expander for credits
with st.sidebar.expander("Credits"):
    st.write("This app was developed by Daniel Rosehill.")

# Filter data for selected companies
filtered_data = data[data['company_name'].isin(selected_companies)]

# Calculate monetized emissions intensity ratio for each selected company
if not filtered_data.empty:
    filtered_data['monetized_emissions_intensity_ratio'] = filtered_data.apply(calculate_monetized_emissions_intensity_ratio, axis=1)
    filtered_data['total_emissions'] = (filtered_data['scope_1_emissions'] + filtered_data['scope_2_emissions'] + filtered_data['scope_3_emissions'])
    filtered_data['total_emissions_formatted'] = filtered_data['total_emissions'].apply(lambda x: f"{x:.2f} MTCO2E")
    filtered_data['monetized_all_scope_emissions'] = (filtered_data['scope_1_emissions'] + filtered_data['scope_2_emissions'] + filtered_data['scope_3_emissions']) * 236_000_000 / 1_000_000_000  # Convert to billions
    filtered_data['ebitda_minus_monetized_emissions'] = filtered_data['ebitda_2022'] - filtered_data['monetized_all_scope_emissions']

# Tabs
tab1, tab2, tab3 = st.tabs(["Emissions Breakdown by Scope", "Emissions to EBITDA Ratio", "EBITDA minus Emissions"])

# Tab 1: Emissions Breakdown by Scope
with tab1:
    st.subheader('Emissions Breakdown by Scope')
    if not filtered_data.empty:
        # Bar chart for emissions by scope
        companies = filtered_data['company_name']
        scope_1_values = filtered_data['scope_1_emissions']
        scope_2_values = filtered_data['scope_2_emissions']
        scope_3_values = filtered_data['scope_3_emissions']

        x = np.arange(len(companies))  # the label locations
        width = 0.25  # the width of the bars

        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width, scope_1_values, width, label='Scope 1 Emissions', color='blue')
        bars2 = ax.bar(x, scope_2_values, width, label='Scope 2 Emissions', color='green')
        bars3 = ax.bar(x + width, scope_3_values, width, label='Scope 3 Emissions', color='orange')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel('Company')
        ax.set_ylabel('Emissions (MTCO2E)')
        ax.set_title('Emissions Breakdown by Scope')
        ax.set_xticks(x)
        ax.set_xticklabels(companies, rotation=45, ha='right')
        ax.legend()

        # Add value labels on top of the bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)

        st.pyplot(fig)
    else:
        st.write('No data to plot. Please select companies from the sidebar.')

    # Emissions Breakdown by Scope Table
    if not filtered_data.empty:
        emissions_breakdown = filtered_data[['company_name', 'scope_1_emissions', 'scope_2_emissions', 'scope_3_emissions', 'total_emissions_formatted']]
        emissions_breakdown.columns = ['Company', 'Scope 1 Emissions (MTCO2E)', 'Scope 2 Emissions (MTCO2E)', 'Scope 3 Emissions (MTCO2E)', 'Total Emissions (MTCO2E)']
        st.table(emissions_breakdown)
    else:
        st.write('No emissions breakdown available. Please select companies from the sidebar.')

# Tab 2: Emissions to EBITDA Ratio
with tab2:
    st.subheader('Emissions to EBITDA Ratio')
    if not filtered_data.empty:
        companies = filtered_data['company_name']
        monetized_emissions_intensity_ratio_values = filtered_data['monetized_emissions_intensity_ratio']

        x = np.arange(len(companies))  # the label locations

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(x, monetized_emissions_intensity_ratio_values, color='purple')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel('Company')
        ax.set_ylabel('Emissions to EBITDA Ratio')
        ax.set_title('Emissions to EBITDA Ratio')
        ax.set_xticks(x)
        ax.set_xticklabels(companies, rotation=45, ha='right')

        # Add value labels on top of the bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.4f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        add_value_labels(bars)

        st.pyplot(fig)
    else:
        st.write('No data to plot. Please select companies from the sidebar.')

    # Emissions versus Financial Performance Table
    if not filtered_data.empty:
        st.subheader('Emissions versus Financial Performance')
        financial_performance = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 'ebitda_minus_monetized_emissions']]
        financial_performance.columns = ['Company', 'EBITDA (in Billions)', 'Monetized All Scope Emissions (in Billions)', 'EBITDA minus Monetized Emissions (in Billions)']
        financial_performance['EBITDA (in Billions)'] = financial_performance['EBITDA (in Billions)'].apply(lambda x: f"${x:.2f}B")
        financial_performance['Monetized All Scope Emissions (in Billions)'] = financial_performance['Monetized All Scope Emissions (in Billions)'].apply(lambda x: f"${x:.2f}B")
        financial_performance['EBITDA minus Monetized Emissions (in Billions)'] = financial_performance['EBITDA minus Monetized Emissions (in Billions)'].apply(lambda x: f"${x:.2f}B")
        st.table(financial_performance)
    else:
        st.write('No financial performance data available. Please select companies from the sidebar.')

# Tab 3: EBITDA minus Emissions
with tab3:
    st.subheader('EBITDA minus Emissions')
    if not filtered_data.empty:
        companies = filtered_data['company_name']
        ebitda_values = filtered_data['ebitda_2022']
        monetized_emissions_values = filtered_data['monetized_all_scope_emissions']

        x = np.arange(len(companies))  # the label locations
        width = 0.5  # the width of the bars

        fig, ax = plt.subplots(figsize=(10, 5))
        bars1 = ax.bar(x, ebitda_values, width, label='EBITDA', color='green')
        bars2 = ax.bar(x, -monetized_emissions_values, width, label='Monetized Emissions', color='red', bottom=0)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel('Company')
        ax.set_ylabel('Value in Billions of US Dollars')
        ax.set_title('EBITDA minus Emissions')
        ax.set_xticks(x)
        ax.set_xticklabels(companies, rotation=45, ha='right')
        ax.axhline(0, color='black', linewidth=0.8)
        ax.legend()

        # Add value labels on top of the bars
        def add_value_labels(bars, offset):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'${height:.2f}B',
                            xy=(bar.get_x() + bar.get_width() / 2, height + offset),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        add_value_labels(bars1, 0.05)
        add_value_labels(bars2, -0.05)

        st.pyplot(fig)
    else:
        st.write('No data to plot. Please select companies from the sidebar.')

# Source Data
st.subheader('Source Data')
if not filtered_data.empty:
    source_data = filtered_data[['company_name', 'ebitda_2022', 'monetized_all_scope_emissions', 'total_emissions_formatted']]
    source_data.columns = ['Company Name', 'EBITDA', 'Monetized All Scope Emissions', 'Total Emissions']
    source_data['EBITDA'] = source_data['EBITDA'].apply(lambda x: f"${x:.2f}B")
    source_data['Monetized All Scope Emissions'] = source_data['Monetized All Scope Emissions'].apply(lambda x: f"${x:.2f}B")
    st.dataframe(source_data)
else:
    st.write('Please select companies from the sidebar to view the source data.')