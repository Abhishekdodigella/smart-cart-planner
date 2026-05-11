import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒", layout="wide")

# --- TYPO PROOFING ---
# This looks for your file even if it's named 'extenison.zip' on GitHub
ZIP_FILE = "extenison.zip" if os.path.exists("extenison.zip") else "extension.zip"

st.title("🛍️ Smart Shopping Plan")

# Extension Download Sidebar
with st.sidebar:
    st.header("Install Tool")
    if os.path.exists(ZIP_FILE):
        with open(ZIP_FILE, "rb") as f:
            st.download_button("📥 Download Extension", f, file_name="smart_cart.zip")
    else:
        st.error("Extension file missing on GitHub!")
    
    st.divider()
    budget = st.number_input("Monthly Budget (₹)", value=5000, step=500)

# Data Processing
params = st.query_params
if "cart_data" in params:
    try:
        items = json.loads(params["cart_data"])
        df = pd.DataFrame(items)
        
        st.success(f"Captured {len(df)} items!")
        
        # Display Results
        col1, col2 = st.columns(2)
        total_price = df['price'].sum()
        
        with col1:
            st.subheader("Your Items")
            st.dataframe(df[['name', 'price']], use_container_width=True)
            
        with col2:
            st.metric("Total Value", f"₹{total_price}")
            if total_price > budget:
                st.error(f"You are ₹{total_price - budget} over budget!")
            else:
                st.success("You are within budget!")
                
    except Exception as e:
        st.error("Data error. Try clicking the extension again.")
else:
    st.info("👋 Open your Amazon Cart and click the 'Smart Cart' extension to begin!")
