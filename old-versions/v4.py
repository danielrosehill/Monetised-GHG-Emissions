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
    st.write("This app was developed by Daniel Rosehill - danielrosehill.com.")

# Filter data for selected companies
filtered_data = data[data['company_name'].isin(selected_companies)]

# Calculate monetized emissions intensity ratio for each selected company
if not filtered_data.empty:
    filtered_data['monetized_emissions_intensity_ratio'] = filtered_data.apply(calculate_monetized_emissions_intensity_ratio, axis=1)
    filtered_data['total_emissions'] = (filtered_data['scope_1_emissions'] + filtered_data['scope_2_emissions'] + filtered_data['scope_3_emissions'])
    filtered_data['total_emissions_formatted'] = filtered_data['total_emissions'].apply(lambda x: f"{x:.2f} MTCO2E")
    filtered_data['monetized_all_scope_emissions'] = (filtered_data['scope_1_emissions'] + filtered_data['scope_2_emissions'] + filtered_data['scope_3_emissions']) * 236_000_000 / 1_000_000_000  # Convert to billions

# Tabs
tab1, tab2 = st.tabs(["Monetized Emissions Intensity Ratio", "EBITDA versus Monetized Emissions"])

# Tab 1: Monetized Emissions Intensity Ratio
with tab1:
    st.subheader('Selected Companies and Metrics')
    if not filtered_data.empty:
        st.table(filtered_data[['company_name', 'monetized_emissions_intensity_ratio']])
    else:
        st.write('Please select companies from the sidebar to view their metrics.')

    st.subheader('Monetized Emissions Intensity Ratio')
    if not filtered_data.empty:
        fig, ax = plt.subplots()
        ax.bar(filtered_data['company_name'], filtered_data['monetized_emissions_intensity_ratio'])
        ax.set_xlabel('Company Name')
        ax.set_ylabel('Monetized Emissions Intensity Ratio')
        ax.set_title('Monetized Emissions Intensity Ratio by Company')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    else:
        st.write('No data to plot. Please select companies from the sidebar.')

# Tab 2: EBITDA versus Monetized Emissions
with tab2:
    st.subheader('EBITDA versus Monetized Emissions')
    if not filtered_data.empty:
        companies = filtered_data['company_name']
        ebitda_values = filtered_data['ebitda_2022']
        monetized_emissions_values = filtered_data['monetized_all_scope_emissions']

        x = np.arange(len(companies))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots(figsize=(10, 5))
        bars1 = ax.bar(x - width/2, ebitda_values, width, label='EBITDA', color='blue')
        bars2 = ax.bar(x + width/2, monetized_emissions_values, width, label='Monetized Emissions', color='orange')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel('Company Name')
        ax.set_ylabel('Value in Billions of US Dollars')
        ax.set_title('EBITDA versus Monetized Emissions')
        ax.set_xticks(x)
        ax.set_xticklabels(companies, rotation=45, ha='right')
        ax.legend()

        # Add value labels on top of the bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'${height:.2f}B',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        add_value_labels(bars1)
        add_value_labels(bars2)

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