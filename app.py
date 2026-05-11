import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. INITIAL PAGE CONFIG ---
st.set_page_config(
    page_title="Smart Cart Planner", 
    page_icon="🛍️", 
    layout="wide"
)

# --- 2. THE TYPO-FIXER ---
# This checks for both 'extension.zip' and your GitHub typo 'extenison.zip'
# This prevents the "FileNotFoundError" you were seeing.
ZIP_FILE_NAME = "extenison.zip" if os.path.exists("extenison.zip") else "extension.zip"

# --- 3. CUSTOM STYLING (CSS) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ANALYTICS LOGIC ---
def get_current_season():
    month = datetime.now().month
    if 3 <= month <= 6: return "Summer"
    if 7 <= month <= 9: return "Monsoon"
    if 10 <= month <= 11: return "Autumn"
    return "Winter"

def analyze_item_season(name):
    name = str(name).lower()
    winter_keywords = ['jacket', 'sweater', 'hoodie', 'wool', 'coat', 'blanket', 'heater', 'boots']
    summer_keywords = ['t-shirt', 'shorts', 'ac', 'cooler', 'cotton', 'fan', 'sandals', 'sunscreen']
    
    if any(word in name for word in winter_keywords): return "Winter"
    if any(word in name for word in summer_keywords): return "Summer"
    return "All-Season"

# --- 5. SIDEBAR ---
st.sidebar.header("⚙️ Budget Settings")
user_budget = st.sidebar.number_input("Enter Monthly Budget (₹)", min_value=0, value=5000, step=500)
st.sidebar.info(f"Current System Season: **{get_current_season()}**")

# --- 6. MAIN INTERFACE ---
st.title("🛍️ Smart Shopping Plan")
st.write("Optimize your cart based on priority, budget, and season.")

# Extension Download Section
with st.expander("📥 First time here? Install the Chrome Extension"):
    st.write("To pull items automatically from Amazon/Myntra, download this tool:")
    if os.path.exists(ZIP_FILE_NAME):
        with open(ZIP_FILE_NAME, "rb") as f:
            st.download_button(
                label="Download Extension Zip",
                data=f,
                file_name="smart_cart_extension.zip",
                mime="application/zip"
            )
        st.caption("Steps: Unzip -> chrome://extensions -> Developer Mode -> Load Unpacked.")
    else:
        st.error(f"Critical Error: Zip file not found in repository. Please upload {ZIP_FILE_NAME}.")

# --- 7. DATA PROCESSING ---
query_params = st.query_params

if "cart_data" in query_params:
    try:
        # Decode data from Extension
        raw_data = json.loads(query_params["cart_data"])
        df = pd.DataFrame(raw_data)
        
        # Clean Prices (Removing commas if they exist)
        df['price'] = df['price'].apply(lambda x: float(str(x).replace(',', '')))
        
        st.success(f"✅ Successfully captured {len(df)} items!")

        # Priority Sorting (Cheapest items first to maximize quantity)
        df = df.sort_values(by='price')
        
        # Budget Analysis
        current_balance = user_budget
        buy_list = []
        wait_list = []
        
        for _, item in df.iterrows():
            item_season = analyze_item_season(item['name'])
            current_sys_season = get_current_season()
            
            # Logic: Can we afford it AND is it the right season?
            if item['price'] <= current_balance and (item_season == current_sys_season or item_season == "All-Season"):
                buy_list.append(item)
                current_balance -= item['price']
            else:
                reason = "Out of Budget" if item['price'] > current_balance else f"Wrong Season ({item_season})"
                item_with_reason = item.to_dict()
                item_with_reason['reason'] = reason
                wait_list.append(item_with_reason)

        # Display Results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Recommended to Buy")
            if buy_list:
                for item in buy_list:
                    with st.container(border=True):
                        st.write(f"**{item['name']}**")
                        st.write(f"₹{item['price']}")
            else:
                st.write("No items fit the current budget/season.")

        with col2:
            st.subheader("⏳ Save for Later")
            if wait_list:
                for item in wait_list:
                    with st.expander(f"{item['name'][:40]}..."):
                        st.write(f"Price: ₹{item['price']}")
                        st.write(f"Reason: {item['reason']}")

        st.divider()
        st.metric("Remaining Balance", f"₹{current_balance}")

    except Exception as e:
        st.error(f"Error processing cart: {e}")
else:
    st.info("👋 Open your Amazon Cart and click the 'Analyze' extension button to begin!")
