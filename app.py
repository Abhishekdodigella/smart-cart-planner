import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒")

# --- FILE PATH FIX ---
# This looks for your file regardless of the typo on GitHub
ZIP_PATH = "extenison.zip" if os.path.exists("extenison.zip") else "extension.zip"

st.title("🛍️ Your Smart Shopping Plan")

# Extension Download Section
with st.expander("🚀 Install the Tool"):
    if os.path.exists(ZIP_PATH):
        with open(ZIP_PATH, "rb") as f:
            st.download_button("📥 Download Extension Zip", f, file_name="smart_cart_extension.zip")
        st.write("Extract the zip, go to `chrome://extensions`, enable 'Developer Mode', and 'Load Unpacked'.")
    else:
        st.error(f"Error: Neither 'extension.zip' nor 'extenison.zip' was found in your GitHub repo.")

# Data Handling
query_params = st.query_params
if "cart_data" in query_params:
    try:
        data = json.loads(query_params["cart_data"])
        st.success(f"Successfully loaded {len(data)} items!")
        df = pd.DataFrame(data)
        st.table(df)
        
        budget = st.number_input("Enter your Budget (₹)", value=5000)
        total = df['price'].sum()
        st.metric("Total Cart Value", f"₹{total}")
        
        if total > budget:
            st.warning(f"You are ₹{total - budget} over budget!")
    except Exception as e:
        st.error("Failed to parse data.")
else:
    st.info("👋 Open your Amazon cart and click the extension to start!")
