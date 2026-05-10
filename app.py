import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# --- CONFIG ---
st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒", layout="wide")

# --- AUTO-SEASON LOGIC ---
def detect_season_from_name(name):
    name = str(name).lower()
    winter_words = ['sweater', 'jacket', 'wool', 'hoodie', 'coat', 'blanket', 'heater', 'winter', 'boots']
    summer_words = ['t-shirt', 'shorts', 'ac', 'cooler', 'sunscreen', 'cotton', 'fan', 'summer', 'sandals']
    
    if any(word in name for word in winter_words): return "Winter"
    if any(word in name for word in summer_words): return "Summer"
    return "All"

def get_current_season():
    month = datetime.now().month
    if 3 <= month <= 6: return "Summer"
    if 7 <= month <= 9: return "Monsoon"
    if 10 <= month <= 11: return "Autumn"
    return "Winter"

# --- MAIN ANALYSIS ENGINE ---
def analyze_cart(items, budget):
    current_season = get_current_season()
    buy, wait = [], []
    # Clean data: Ensure price is numeric
    for item in items:
        try:
            item['price'] = float(str(item.get('price', 0)).replace(',', ''))
        except:
            item['price'] = 0
            
    # Sort items by price (cheapest first)
    items = sorted(items, key=lambda x: x['price'])
    
    rem_budget = budget
    for item in items:
        item_season = detect_season_from_name(item.get('name', 'Unknown'))
        
        if item['price'] <= rem_budget:
            if item_season == current_season or item_season == "All":
                buy.append(item)
                rem_budget -= item['price']
            else:
                item['reason'] = f"Wrong Season ({item_season})"
                wait.append(item)
        else:
            item['reason'] = "Exceeds budget"
            wait.append(item)
            
    return buy, wait, rem_budget

# --- UI START ---
st.title("🛍️ Smart Shopping Plan")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("⚙️ Budget Settings")
budget = st.sidebar.number_input("Set Your Budget (₹)", min_value=0, value=5000, step=500)
st.sidebar.info(f"Current Season: **{get_current_season()}**")

# --- STEP 1: EXTENSION DOWNLOAD ---
with st.expander("📥 Install the Extension (Recommended)"):
    st.write("For a one-click experience, use our Chrome Extension.")
    # Check for both possible filenames due to the typo
    zip_fn = "extenison.zip" if os.path.exists("extenison.zip") else "extension.zip"
    if os.path.exists(zip_fn):
        with open(zip_fn, "rb") as f:
            st.download_button("Download Extension Tool", f, file_name="smart_cart.zip")
    else:
        st.warning("Extension zip file not found on GitHub. Please upload it!")

# --- STEP 2: DATA INPUT ---
cart_items = []
query_params = st.query_params

if "cart_data" in query_params:
    # DATA FROM EXTENSION
    try:
        cart_items = json.loads(query_params["cart_data"])
        st.success(f"✅ Captured {len(cart_items)} items from your browser!")
    except:
        st.error("Error reading extension data.")
else:
    # DATA FROM CSV UPLOAD
    st.divider()
    uploaded_file = st.file_uploader("Or upload your cart CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Fuzzy Column Mapping
        col_map = {col.lower(): col for col in df.columns}
        final_df = pd.DataFrame()
        
        # Try to find Name and Price columns regardless of exact spelling
        name_col = next((v for k, v in col_map.items() if 'name' in k or 'title' in k or 'item' in k), None)
        price_col = next((v for k, v in col_map.items() if 'price' in k or 'mrp' in k or 'amount' in k or 'value' in k), None)
        
        if name_col and price_col:
            final_df['name'] = df[name_col]
            final_df['price'] = df[price_col]
            cart_items = final_df.to_dict('records')
        else:
            st.error("Could not find 'Name' or 'Price' columns in your CSV.")

# --- STEP 3: RESULTS ---
if cart_items:
    buy_list, wait_list, balance = analyze_cart(cart_items, budget)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Recommended to Buy")
        for item in buy_list:
            with st.container(border=True):
                st.write(f"**{item['name']}**")
                st.write(f"₹{item['price']}")

    with col2:
        st.subheader("⏳ Save for Later")
        for item in wait_list:
            with st.expander(f"{item['name']} (₹{item['price']})"):
                st.write(f"**Reason:** {item.get('reason', 'N/A')}")

    st.divider()
    st.metric("Remaining Budget", f"₹{balance}")
else:
    st.info("No items to show. Use the extension or upload a CSV to begin.")
