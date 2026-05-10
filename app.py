import streamlit as st
import pandas as pd
import json
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Smart Cart Planner", page_icon="🛒", layout="wide")

# --- AUTO-SEASON LOGIC ---
def detect_season_from_name(name):
    name = name.lower()
    winter_words = ['sweater', 'jacket', 'wool', 'hoodie', 'coat', 'blanket', 'heater', 'muffler', 'gloves']
    summer_words = ['t-shirt', 'shorts', 'ac', 'cooler', 'sunscreen', 'sleeveless', 'cotton', 'fan', 'sunglasses']
    
    if any(word in name for word in winter_words):
        return "Winter"
    if any(word in name for word in summer_words):
        return "Summer"
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
    # Sort by price (cheapest first to maximize items) or discount if available
    items = sorted(items, key=lambda x: x['price'])
    
    rem_budget = budget
    for item in items:
        item_season = detect_season_from_name(item['name'])
        
        # Logic: If it's the right season AND fits in budget
        if item['price'] <= rem_budget:
            if item_season == current_season or item_season == "All":
                buy.append(item)
                rem_budget -= item['price']
            else:
                item['reason'] = f"Off-season purchase ({item_season} item in {current_season})"
                wait.append(item)
        else:
            item['reason'] = "Exceeds remaining budget"
            wait.append(item)
            
    return buy, wait, rem_budget

# --- UI ---
st.title("🛍️ Your Smart Shopping Plan")

# LISTEN FOR EXTENSION DATA
# The extension sends data to: your-url/?cart_data=[...]
query_params = st.query_params

if "cart_data" in query_params:
    try:
        raw_data = query_params["cart_data"]
        cart_items = json.loads(raw_data)
        
        st.sidebar.success(f"✅ Received {len(cart_items)} items from your cart!")
        budget = st.sidebar.number_input("Set your Budget (₹)", min_value=0, value=5000, step=500)
        
        buy_list, wait_list, balance = analyze_cart(cart_items, budget)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Recommended to Buy Now")
            for item in buy_list:
                with st.container(border=True):
                    st.write(f"**{item['name']}**")
                    st.write(f"Price: ₹{item['price']}")
                    st.caption(f"Source: {item.get('site', 'Online Store')}")

        with col2:
            st.subheader("⏳ Better to Wait")
            for item in wait_list:
                with st.expander(f"{item['name']} (₹{item['price']})"):
                    st.write(f"**Reason:** {item['reason']}")
                    st.write("Our advice: Save this for a better time or higher budget.")
                    
        st.divider()
        st.metric("Remaining Budget", f"₹{balance}")

    except Exception as e:
        st.error(f"Error reading cart data. Make sure the extension is updated.")
else:
    st.info("👋 To start, open your Amazon/Myntra cart and click your 'Smart Cart' Extension!")
    st.image("https://img.icons8.com/illustrations/external-tulpahn-outline-color-tulpahn/100/external-online-shopping-ecommerce-tulpahn-outline-color-tulpahn.png", width=200)
with open("extension.zip", "rb") as fp:
    btn = st.download_button(
        label="📥 Download Chrome Extension to Start",
        data=fp,
        file_name="smart-cart-extension.zip",
        mime="application/zip"
    )
st.caption("After downloading, unzip and load via chrome://extensions in Developer Mode.")
