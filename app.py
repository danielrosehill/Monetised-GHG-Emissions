import streamlit as st
import csv
from io import StringIO

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = {}

if 'config' not in st.session_state:
    st.session_state.config = {'csv_path': 'emissions_data.csv'}

def calculate_values():
    try:
        scope1 = float(st.session_state.scope_one_input)
        scope2 = float(st.session_state.scope_two_input)
        scope3 = float(st.session_state.scope_three_input)
        ebitda = float(st.session_state.ebitda_input)
        ebitda_unit = st.session_state.ebitda_unit_combo
        
        total_emissions = scope1 + scope2 + scope3
        total_scope12_emissions = scope1 + scope2
        monetized_scope12 = total_scope12_emissions * 236 * 1_000_000
        monetized_total_emissions = total_emissions * 236 * 1_000_000
        
        if ebitda_unit == "BN":
            ebitda *= 1_000_000_000
        elif ebitda_unit == "MN":
            ebitda *= 1_000_000
        
        ebitda_minus_emissions = ebitda - monetized_total_emissions
        emissions_intensity_ratio = monetized_total_emissions / ebitda if ebitda != 0 else 0
        emissions_intensity_percentage = emissions_intensity_ratio * 100
        
        # Format monetized values for display
        monetized_scope12_display = format_monetized_value(monetized_scope12)
        monetized_total_emissions_display = format_monetized_value(monetized_total_emissions)
        
        st.session_state.total_emissions_value = f"{total_emissions:.2f} million tons of CO2e"
        st.session_state.total_scope12_emissions_value = f"{total_scope12_emissions:.2f} million tons of CO2e"
        st.session_state.monetized_scope12_value = f"${monetized_scope12_display} ({monetized_scope12:,.2f})"
        st.session_state.monetized_total_emissions_value = f"${monetized_total_emissions_display} ({monetized_total_emissions:,.2f})"
        st.session_state.ebitda_minus_emissions_value = f"${ebitda_minus_emissions:,.2f}"
        st.session_state.emissions_intensity_value = f"{emissions_intensity_ratio:.2f}"
        st.session_state.emissions_intensity_percentage_value = f"{emissions_intensity_percentage:.2f}%"
        
        st.session_state.data = {
            'Company Name': st.session_state.company_name_input,
            'Emissions Reporting Year': st.session_state.reporting_year_input,
            'Emissions Report URL': st.session_state.emissions_report_url_input,
            'EBITDA Report URL': st.session_state.ebitda_report_url_input,
            'Scope One Emissions': scope1,
            'Scope Two Emissions': scope2,
            'Scope Three Emissions': scope3,
            'Total Emissions': total_emissions,
            'Total Scope 1 & 2 Emissions': total_scope12_emissions,
            'Monetized Scope 1 & 2 Emissions': monetized_scope12,
            'Monetized Total Emissions': monetized_total_emissions,
            'EBITDA': ebitda,
            'EBITDA Minus Total Monetized Emissions': ebitda_minus_emissions,
            'Emissions Intensity Ratio': emissions_intensity_ratio,
            'Emissions Intensity Percentage': emissions_intensity_percentage
        }
    except ValueError:
        st.error("Please enter valid numeric values for emissions and EBITDA.")

def format_monetized_value(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    else:
        return f"{value / 1_000_000:.2f}M"

def generate_csv():
    if not st.session_state.data:
        st.error("Please calculate values first.")
        return
    
    headers = st.session_state.data.keys()
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerow(st.session_state.data)
    csv_data = output.getvalue()
    
    st.session_state.csv_header_row = ','.join(headers)
    st.session_state.csv_data_row = csv_data.split('\n')[1]

def clear_fields():
    for key in st.session_state.keys():
        if key.endswith('_input') or key.endswith('_value'):
            st.session_state[key] = ''

def copy_to_clipboard(text):
    js_code = f"""
    navigator.clipboard.writeText(`{text}`);
    alert("Copied to clipboard: {text}");
    """
    st.components.v1.html(f"<button onclick='{js_code}'>Copy to Clipboard</button>", height=32)

# Title and Description
st.title("Monetized GHG Emissions Calculator")
st.text("""
This utility takes GHG emissions as reported by companies and converts them into monetary terms 
at the rate of $236 per ton of carbon dioxide equivalents proposed by the International Foundation 
for Valuing Units. Please ensure that the input fields are denominated in this unit only and select 
the correct reporting unit for EBITDA (Earnings Before Interest, Tax, Depreciation, and Amortization). 
The calculator will calculate the emissions intensity ratio which is the monetized emissions divided 
by the EBITDA and it will express it as a percentage as well. To copy the data out of this utility, 
use the CSV data row which is generated below the data table.
""")

# Layout with two columns
col1, col2 = st.columns([1, 1.2])

# Left Column - Input Fields
with col1:
    st.subheader("Input Fields")
    st.text_input("Company Name:", key='company_name_input')
    st.text_input("Emissions Reporting Year:", key='reporting_year_input')
    st.text_input("Emissions Report URL:", key='emissions_report_url_input')
    st.text_input("EBITDA Report URL:", key='ebitda_report_url_input')
    st.text_input("Scope One Emissions (in millions of tons of CO2e):", key='scope_one_input')
    st.text_input("Scope Two Emissions (in millions of tons of CO2e):", key='scope_two_input')
    st.text_input("Scope Three Emissions (in millions of tons of CO2e):", key='scope_three_input')
    st.text_input("EBITDA:", key='ebitda_input')
    st.selectbox("EBITDA Unit:", options=["BN", "MN"], key='ebitda_unit_combo')
    st.button("Calculate", on_click=calculate_values)
    st.button("Generate CSV", on_click=generate_csv)
    st.button("Clear", on_click=clear_fields)

# Vertical Divider
st.markdown("<style>.stVerticalBlock {display: flex; align-items: stretch; gap: 20px;}</style>", unsafe_allow_html=True)
st.markdown("<div style='width: 2px; background-color: #ccc;'></div>", unsafe_allow_html=True)

# Right Column - Calculated Values
with col2:
    st.subheader("Calculated Values")
    
    st.markdown(f"**Total Emissions (Scope 1 + 2 + 3):**")
    st.markdown(f"{st.session_state.get('total_emissions_value', '')}")
    
    st.markdown(f"**Total Scope 1 & 2 Emissions:**")
    st.markdown(f"{st.session_state.get('total_scope12_emissions_value', '')}")
    
    st.markdown(f"**Monetized Scope 1 & 2 Emissions ($):**")
    st.markdown(f"{st.session_state.get('monetized_scope12_value', '')}")
    
    st.markdown(f"**Monetized Total Emissions ($):**")
    st.markdown(f"{st.session_state.get('monetized_total_emissions_value', '')}")
    
    st.markdown(f"**EBITDA - Total Monetized Emissions ($):**")
    st.markdown(f"{st.session_state.get('ebitda_minus_emissions_value', '')}")
    
    st.markdown(f"**Emissions Intensity Ratio:**")
    st.markdown(f"{st.session_state.get('emissions_intensity_value', '')}")
    
    st.markdown(f"**Emissions Intensity Percentage (%):**")
    st.markdown(f"{st.session_state.get('emissions_intensity_percentage_value', '')}")

# CSV Output
st.subheader("CSV Output")
csv_header_row = st.session_state.get('csv_header_row', '')
csv_data_row = st.session_state.get('csv_data_row', '')

col3, col4 = st.columns(2)

with col3:
    st.text_area("CSV Header Row:", value=csv_header_row, key='csv_header_row', disabled=True, height=100)
    copy_to_clipboard(csv_header_row)

with col4:
    st.text_area("CSV Data Row:", value=csv_data_row, key='csv_data_row', disabled=True, height=100)
    copy_to_clipboard(csv_data_row)