import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="My Smart Cart", page_icon="🛒", layout="wide")

def get_season():
    month = datetime.now().month
    if 3 <= month <= 6: return "Summer"
    if 7 <= month <= 9: return "Monsoon"
    if 10 <= month <= 11: return "Autumn"
    return "Winter"

def analyze_cart(df, budget):
    current_season = get_season()
    buy, wait = [], []
    # Sort by highest discount first
    df = df.sort_values(by='discount', ascending=False)
    rem_budget = budget

    for _, item in df.iterrows():
        if item['price'] <= rem_budget and (item['season'] == current_season or item['season'] == "All"):
            buy.append(item)
            rem_budget -= item['price']
        else:
            reason = "Exceeds Budget" if item['price'] > rem_budget else f"Off-season ({item['season']})"
            item_dict = item.to_dict()
            item_dict['reason'] = reason
            wait.append(item_dict)
    return buy, wait, rem_budget

# --- UI ---
st.title("🛒 My Personal Cart Planner")
st.sidebar.header("Step 1: Set Budget")
budget = st.sidebar.number_input("Your Budget (₹)", min_value=0, value=5000)

st.write("### Step 2: Upload your Cart CSV")
uploaded_file = st.file_uploader("Upload the CSV file you exported from your cart", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Check if CSV has right columns
    required_columns = ['name', 'price', 'discount', 'season', 'site']
    if all(col in df.columns for col in required_columns):
        if st.button("Calculate Best Buys"):
            buy_list, wait_list, balance = analyze_cart(df, budget)
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"✅ Buy These (Remaining: ₹{balance})")
                for item in buy_list:
                    st.info(f"**{item['name']}** from {item['site']}\n\nPrice: ₹{item['price']} ({item['discount']}% off)")
            
            with col2:
                st.warning("⏳ Wait on These")
                for item in wait_list:
                    with st.expander(f"{item['name']} (₹{item['price']})"):
                        st.write(f"**Reason:** {item['reason']}")
                        st.write("Suggested: Buy this during " + item['season'])
    else:
        st.error(f"Your CSV must have these headers: {', '.join(required_columns)}")
else:
    st.info("Waiting for your cart file...")
