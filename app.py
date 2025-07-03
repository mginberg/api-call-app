import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Chase API Subcampaign Lookup", layout="centered")

st.title("📞 Chase API Subcampaign Lookup")

st.markdown("""
Upload a CSV file with a **phone** column.  
The app will query the Chase API for each phone number and output the Subcampaign.  
If any lead is in **HappyQuote**, that will be used.
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
        data = response.json()
    except Exception as e:
        return f"ERROR: {e}"

    leads = data.get("Leads")
    if not leads:
        return "NOT FOUND"

    subcampaigns = [lead.get("Subcampaign", "UNKNOWN") for lead in leads]

    if "HappyQuote" in subcampaigns:
        return "HappyQuote"
    else:
        return subcampaigns[0]

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if 'phone' not in df.columns:
        st.error("The CSV must contain a column named 'phone'.")
    else:
        if st.button("Run Lookup"):
            st.info("Processing lookups... This may take a minute.")
            results = []
            for phone in df['phone']:
                sub = lookup_subcampaign(phone)
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
