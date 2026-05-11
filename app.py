import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒", layout="wide")

# --- TYPO-PROOFING FOR GITHUB ---
# This looks for your zip file even if it's named 'extenison.zip' on GitHub
ZIP_PATH = "extenison.zip" if os.path.exists("extenison.zip") else "extension.zip"

# --- STYLING ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def get_current_season():
    month = datetime.now().month
    if 3 <= month <= 6: return "Summer"
    if 7 <= month <= 9: return "Monsoon"
    if 10 <= month <= 11: return "Autumn"
    return "Winter"

def detect_season(name):
    name = str(name).lower()
    winter_words = ['sweater', 'jacket', 'wool', 'hoodie', 'coat', 'blanket', 'heater', 'winter']
    summer_words = ['t-shirt', 'shorts', 'ac', 'cooler', 'sunscreen', 'cotton', 'fan', 'summer']
    if any(w in name for w in winter_words): return "Winter"
    if any(w in name for w in summer_words): return "Summer"
    return "All"

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("⚙️ Budget Settings")
budget = st.sidebar.number_input("Set Your Monthly Budget (₹)", min_value=0, value=5000, step=500)
st.sidebar.info(f"System Season: **{get_current_season()}**")

# --- MAIN UI ---
st.title("🛍️ Smart Shopping Plan")

# STEP 1: Extension Download for New Users
with st.expander("🚀 First time? Download the Chrome Extension"):
    st.write("To scan your cart automatically, you need our helper tool:")
    if os.path.exists(ZIP_PATH):
        with open(ZIP_PATH, "rb") as f:
            st.download_button(
                label="📥 Download Extension Zip",
                data=f,
                file_name="smart_cart_extension.zip",
                mime="application/zip"
            )
        st.info("How to install: Unzip the file -> Go to `chrome://extensions` -> Enable 'Developer Mode' -> 'Load Unpacked' -> Select the folder.")
    else:
        st.error(f"File not found on GitHub. Please ensure '{ZIP_PATH}' is in your repository.")

# STEP 2: Data Handling
query_params = st.query_params
cart_items = []

if "cart_data" in query_params:
    try:
        # Capture data sent from the extension
        cart_items = json.loads(query_params["cart_data"])
        st.success(f"✅ Captured {len(cart_items)} items from your browser!")
    except Exception as e:
        st.error("Error reading extension data. Please try scanning again.")
else:
    st.divider()
    st.info("👋 Open your Amazon/Myntra cart and click the extension button to see your results here!")

# STEP 3: Analysis and Display
if cart_items:
    current_season = get_current_season()
    buy, wait = [], []
    
    # Process items
    sorted_items = sorted(cart_items, key=lambda x: float(str(x['price']).replace(',', '')))
    remaining = budget
    
    for item in sorted_items:
        price = float(str(item['price']).replace(',', ''))
        season = detect_season(item['name'])
        
        if price <= remaining and (season == current_season or season == "All"):
            buy.append(item)
            remaining -= price
        else:
            item['reason'] = "Exceeds Budget" if price > remaining else f"Wait for {season}"
            wait.append(item)

    # UI Columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Buy Now")
        for item in buy:
            with st.container(border=True):
                st.write(f"**{item['name'][:50]}...**")
                st.write(f"💰 ₹{item['price']}")

    with col2:
        st.subheader("⏳ Wait for Later")
        for item in wait:
            with st.expander(f"{item['name'][:30]}..."):
                st.write(f"**Price:** ₹{item['price']}")
                st.write(f"**Advice:** {item.get('reason', 'Check season')}")

    st.divider()
    st.metric("Remaining Balance", f"₹{remaining}")
