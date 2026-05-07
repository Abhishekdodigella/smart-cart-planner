import streamlit as st
import pandas as pd
import json
from datetime import datetime

# --- CONFIG & SEASON LOGIC ---
st.set_page_config(page_title="One-Click Cart Planner", layout="wide")

def get_season():
    month = datetime.now().month
    if 3 <= month <= 6: return "Summer"
    if 7 <= month <= 9: return "Monsoon"
    if 10 <= month <= 11: return "Autumn"
    return "Winter"

# --- SMART ENGINE ---
def analyze_data(items, budget):
    current_season = get_season()
    buy, wait = [], []
    items = sorted(items, key=lambda x: int(x.get('discount', 0)), reverse=True)
    rem_budget = budget

    for item in items:
        price = int(item.get('price', 0))
        # Simple auto-season detection
        name_lower = item['name'].lower()
        item_season = "Winter" if any(w in name_lower for w in ['sweater', 'jacket', 'wool']) else "Summer" if any(s in name_lower for s in ['t-shirt', 'shorts', 'cotton']) else "All"
        
        if price <= rem_budget and (item_season == current_season or item_season == "All"):
            buy.append(item)
            rem_budget -= price
        else:
            item['reason'] = "Exceeds Budget" if price > rem_budget else f"Wrong Season ({item_season})"
            wait.append(item)
    return buy, wait, rem_budget

# --- UI ---
st.title("🚀 One-Click Cart Planner")

# Get data from the Bookmarklet (sent via URL)
query_params = st.query_params
if "cart_data" in query_params:
    raw_data = query_params["cart_data"]
    cart_items = json.loads(raw_data)
    
    st.sidebar.success("✅ Cart Data Received!")
    budget = st.sidebar.number_input("Set Budget (₹)", value=5000)
    
    buy_list, wait_list, balance = analyze_data(cart_items, budget)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Buy Now")
        for item in buy_list:
            st.info(f"**{item['name']}**\n\n₹{item['price']}")
    with col2:
        st.subheader("⏳ Wait")
        for item in wait_list:
            st.warning(f"**{item['name']}**\n\nReason: {item['reason']}")
else:
    st.info("👋 How to use: Drag the button below to your bookmarks, then click it when you are in your Amazon/Myntra cart!")
    st.markdown('<a href="javascript:(function(){/*Script below goes here*/})()">Analyze My Cart</a>', unsafe_allow_html=True)
