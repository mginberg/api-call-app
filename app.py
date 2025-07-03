import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Chase API Subcampaign Lookup", layout="centered")

st.title("📞 Chase API Subcampaign Lookup")

st.markdown("""
Upload a CSV file with a **phone** column.  
The app will query the Chase API for each phone number and output the Subcampaign.  
If the Subcampaign field is not found, it will show "NOT FOUND".
""")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

API_BASE_URL = (
    "https://api.chasedatacorp.com/HttpImport/LeadOperations.php"
    "?token=9eb5c896-3337-4889-813c-bdb2eb8aa360"
    "&accid=finalexpensesolutions"
    "&Action=SearchLead"
    "&SearchField=Phone"
    "&Detailed=1"
)

def lookup_subcampaign(phone):
    url = f"{API_BASE_URL}&Identifier={phone}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text_data = response.text
    except Exception as e:
        return f"ERROR: {e}"

    # DEBUG: Show the raw text response in Streamlit
    st.write("Raw API response for", phone, ":", text_data)

    # Find the Subcampaign field in the text
    subcampaign = "NOT FOUND"
    pairs = text_data.split('","')
    for pair in pairs:
        if pair.startswith('"Subcampaign":"') or pair.startswith('Subcampaign":"'):
            # Extract everything after the colon and remove quotes
            subcampaign = pair.split('":"')[1].strip('"')
            break

    return subcampaign

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if 'phone' not in df.columns:
        st.error("The CSV must contain a column named 'phone'.")
    else:
        if st.button("Run Lookup"):
            st.info("Processing lookups... This may take a minute.")
            results = []
            for phone in df['phone']:
                sub = lookup_subcampaign(str(phone))
                results.append({"phone": phone, "subcampaign": sub})
            results_df = pd.DataFrame(results)
            st.success("Lookups completed!")
            st.dataframe(results_df)
            csv_data = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name="results.csv",
                mime="text/csv"
            )
