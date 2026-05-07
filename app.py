import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Smart Cart Pro", page_icon="🛍️", layout="wide")

# Custom CSS for a better UI
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    .product-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-left: 5px solid #28a745;
    }
    .wait-card {
        background-color: #fff4f4; padding: 15px; border-radius: 10px;
        border-left: 5px solid #ff4b4b; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
def get_season():
    month = datetime.now().month
    if 3 <= month <= 6: return "Summer"
    if 7 <= month <= 9: return "Monsoon"
    if 10 <= month <= 11: return "Autumn"
    return "Winter"

def analyze_cart(cart_items, budget):
    current_season = get_season()
    buy, wait = [], []
    sorted_items = sorted(cart_items, key=lambda x: x['discount'], reverse=True)
    rem_budget = budget

    for item in sorted_items:
        if item['price'] <= rem_budget and (item['season'] == current_season or item['season'] == "All"):
            buy.append(item)
            rem_budget -= item['price']
        else:
            reason = "Exceeds Budget" if item['price'] > rem_budget else f"Off-season ({item['season']})"
            item['reason'] = reason
            wait.append(item)
    return buy, wait, rem_budget

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.info(f"Current Season: **{get_season()}**")
    budget = st.number_input("Monthly Shopping Budget (₹)", min_value=0, value=10000, step=500)
    st.divider()
    st.write("🔗 **Connected Accounts**")
    st.checkbox("Amazon.in", value=True)
    st.checkbox("Flipkart", value=True)
    st.checkbox("Myntra", value=True)

# --- MAIN UI ---
st.title("🛒 Smart Cart Planner")
st.write("We analyzed your carts to find the best value for your money today.")

# Mock Data
mock_data = [
    {"name": "Air Conditioner", "price": 35000, "discount": 15, "season": "Summer", "site": "Amazon"},
    {"name": "Leather Jacket", "price": 4500, "discount": 60, "season": "Winter", "site": "Myntra"},
    {"name": "Wireless Earbuds", "price": 2999, "discount": 40, "season": "All", "site": "Flipkart"},
    {"name": "Sunscreen SPF 50", "price": 450, "discount": 10, "season": "Summer", "site": "Amazon"},
    {"name": "Coffee Maker", "price": 5500, "discount": 25, "season": "All", "site": "Amazon"},
]

if st.button("Generate My Shopping Plan"):
    buy_list, wait_list, balance = analyze_cart(mock_data, budget)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("✅ Recommended to Buy Now")
        if not buy_list:
            st.write("No items fit your budget/season right now.")
        for item in buy_list:
            st.markdown(f"""
            <div class="product-card">
                <span style="color: #666; font-size: 0.8em;">{item['site']}</span>
                <h3 style="margin: 0;">{item['name']}</h3>
                <p style="color: #28a745; font-weight: bold; font-size: 1.2em;">₹{item['price']} 
                <span style="color: #666; font-size: 0.7em; font-weight: normal;">({item['discount']}% Off)</span></p>
                <span style="background: #e8f5e9; padding: 2px 8px; border-radius: 10px; font-size: 0.8em;">Perfect for {item['season']}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("⏳ Wait for Later")
        st.metric("Remaining Budget", f"₹{balance}")
        for item in wait_list:
            st.markdown(f"""
            <div class="wait-card">
                <p style="margin:0; font-weight: bold;">{item['name']}</p>
                <p style="margin:0; color: #ff4b4b; font-size: 0.8em;">Reason: {item['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
