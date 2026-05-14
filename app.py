import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# --- CONFIG ---
st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒", layout="wide")

# --- CSS FOR STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .stExpander { border: 1px solid #ff4b4b; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTO-SEASON LOGIC ---
def detect_season_from_name(name):
    name = name.lower()
    winter_words = ['sweater', 'jacket', 'wool', 'hoodie', 'coat', 'blanket', 'heater', 'muffler', 'gloves', 'boots', 'thermal']
    summer_words = ['t-shirt', 'shorts', 'ac', 'cooler', 'sunscreen', 'sleeveless', 'cotton', 'fan', 'sunglasses', 'sandals', 'vest']
    
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
    
    # Sort items by price (cheapest first)
    items = sorted(items, key=lambda x: x.get('price', 0))
    
    rem_budget = budget
    for item in items:
        # Ensure price is a float
        try:
            price = float(item['price'])
        except:
            continue

        item_season = detect_season_from_name(item['name'])
        
        if price <= rem_budget:
            if item_season == current_season or item_season == "All":
                buy.append(item)
                rem_budget -= price
            else:
                item['reason'] = f"Wrong Season ({item_season} item in {current_season})"
                wait.append(item)
        else:
            item['reason'] = "Exceeds remaining budget"
            wait.append(item)
            
    return buy, wait, rem_budget

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("⚙️ Settings")
budget = st.sidebar.number_input("Your Monthly Budget (₹)", min_value=0, value=5000, step=500)
st.sidebar.divider()

# --- HEADER ---
st.title("🛍️ Smart Shopping Plan")
st.write(f"Current System Season: **{get_current_season()}**")

# --- STEP 1: DOWNLOAD EXTENSION ---
with st.expander("🚀 New User? Download the Chrome Extension Tool"):
    st.write("To analyze your cart automatically, you need our helper tool:")
    zip_path = "extension.zip" if os.path.exists("extension.zip") else "extenison.zip"
    
    if os.path.exists(zip_path):
        with open(zip_path, "rb") as fp:
            st.download_button(
                label="📥 Download Chrome Extension",
                data=fp,
                file_name="smart-cart-extension.zip",
                mime="application/zip"
            )
    else:
        st.error("Extension file not found on server.")

# --- STEP 2: DATA HANDLING (URL DATA) ---
cart_items = []

# New Streamlit 1.30+ Query Param handling
if "cart_data" in st.query_params:
    try:
        raw_data = st.query_params["cart_data"]
        cart_items = json.loads(raw_data)
        if cart_items:
            st.success(f"✅ Successfully captured {len(cart_items)} items from your cart!")
    except Exception as e:
        st.error(f"Error reading extension data: {e}")
else:
    st.divider()
    st.info("👋 Open Amazon/Myntra/Flipkart cart and click the extension button!")

# Manual CSV Fallback
with st.expander("Or upload a CSV manually"):
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        cart_items = df.to_dict('records')

# --- STEP 3: DISPLAY RESULTS ---
if cart_items:
    buy_list, wait_list, balance = analyze_cart(cart_items, budget)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Buy These Now")
        for item in buy_list:
            with st.container(border=True):
                st.write(f"**{item['name']}**")
                st.write(f"💰 Price: ₹{item['price']}")
                st.caption(f"Source: {item.get('site', 'Unknown')}")

    with col2:
        st.subheader("⏳ Wait for Later")
        for item in wait_list:
            with st.expander(f"{item['name']} (₹{item['price']})"):
                st.write(f"**Reason:** {item['reason']}")
                st.write("💡 Tip: Wait for the correct season or a higher budget.")
                
    st.divider()
    st.metric("Total Left in Budget", f"₹{round(balance, 2)}")
    if balance < 100 and budget > 0:
        st.warning("You have reached your budget limit!")
