import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# --- CONFIG ---
st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .stExpander { border: 1px solid #ff4b4b; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
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

def analyze_cart(items, budget):
    current_season = get_current_season()
    buy, wait = [], []
    items = sorted(items, key=lambda x: x.get('price', 0))
    
    rem_budget = budget
    for item in items:
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

# --- UI ---
st.sidebar.header("⚙️ Settings")
budget = st.sidebar.number_input("Your Monthly Budget (₹)", min_value=0, value=5000, step=500)

st.title("🛍️ Smart Shopping Plan")
st.write(f"Current System Season: **{get_current_season()}**")

cart_items = []

# Handshake with Extension
if "cart_data" in st.query_params:
    try:
        raw_data = st.query_params["cart_data"]
        cart_items = json.loads(raw_data)
        if cart_items:
            st.success(f"✅ Captured {len(cart_items)} items from your cart!")
    except Exception as e:
        st.error(f"Data Sync Error: {e}")
else:
    st.info("👋 Open Amazon/Myntra/Flipkart and click the extension button!")

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
    
    st.divider()
    st.metric("Total Left in Budget", f"₹{round(balance, 2)}")
