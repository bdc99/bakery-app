import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
DATA_FILE = "bakery_history.csv"

# Product List
EVERY_DAY = ["Cinnamon Burst", "Honey Whole Wheat", "Dakota", "Cracked Light Wheat", "Beehive White", "Pumpkin Chip", "Chocolate Cherry", "Chocolate Chip", "Snickerdoodle", "Sugar Cookie", "Pumpkin", "Oatmeal Chip", "Double Chocolate", "Gluten Free", "Cinnamon Rolls"]
ROTATIONS = {
    "Monday": ["Sourdough", "Spinach and Cheese", "Strawberry Rolls", "Bread Pudding"],
    "Tuesday": ["Strawberries and Cream", "Cheddar Bacon Rolls", "Mazurka"],
    "Wednesday": ["Wheat Sourdough", "Strawberry Rolls", "Brownies", "Bread Pudding"],
    "Thursday": ["Strawberries and Cream", "Cheddar Bacon Rolls", "Mazurka"],
    "Saturday": ["Garlic Sourdough"]
}

# Base amounts to bake when you have 0 leftovers
BASE_TARGETS = {
    "Cinnamon Burst": 20, "Honey Whole Wheat": 30, "Dakota": 15, "Cracked Light Wheat": 15,
    "Beehive White": 25, "Pumpkin Chip": 12, "Chocolate Cherry": 10, "Chocolate Chip": 24,
    "Snickerdoodle": 12, "Sugar Cookie": 12, "Pumpkin": 12, "Oatmeal Chip": 12,
    "Double Chocolate": 12, "Gluten Free": 6, "Cinnamon Rolls": 30, "Strawberries and Cream": 15,
    "Spinach and Cheese": 15, "Wheat Sourdough": 15, "Sourdough": 15, "Garlic Sourdough": 15,
    "Strawberry Rolls": 12, "Brownies": 12, "Cheddar Bacon Rolls": 18, "Bread Pudding": 8, "Mazurka": 10
}

st.set_page_config(page_title="Bakery Planner", page_icon="🍞")
st.title("🍞 Daily Bake Planner")

tab1, tab2 = st.tabs(["📝 End of Day Entry", "🧑‍🍳 Tomorrow's Bake List"])

with tab1:
    day_name = datetime.now().strftime("%A")
    st.header(f"Closing: {day_name}")
    
    # Register surplus logic
    surplus = st.number_input("Surplus cash above $100.00", min_value=0.0)
    if surplus > 0:
        st.warning(f"DEPOSIT TO BANK: ${surplus:.2f}")

    revenue = st.number_input("Total Revenue ($)", min_value=0.0)
    
    # Get current menu
    todays_menu = EVERY_DAY + ROTATIONS.get(day_name, [])
    daily_entries = []

    st.subheader("Record Leftovers")
    for item in todays_menu:
        st.write(f"**{item}**")
        c1, c2, c3 = st.columns(3)
        with c1: t0 = st.number_input("Today's Left", min_value=0, key=f"{item}_t0")
        with c2: t1 = st.number_input("Yesterday's", min_value=0, key=f"{item}_t1")
        with c3: t2 = st.number_input("Tossed (2-Day)", min_value=0, key=f"{item}_t2")
        
        # 95% Calculation Logic
        std = BASE_TARGETS.get(item, 10)
        # Formula: Target - (Today's Waste above 5%)
        waste_rate = t0 / std
        tomorrow_adj = round(std * (1 + (0.05 - waste_rate)))
        
        daily_entries.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Item": item, "T0": t0, "T1": t1, "T2": t2, 
            "Next_Bake": tomorrow_adj, "Revenue": revenue
        })

    if st.button("Save & Generate Bake List"):
        df_new = pd.DataFrame(daily_entries)
        if os.path.exists(DATA_FILE):
            df_old = pd.read_csv(DATA_FILE)
            pd.concat([df_old, df_new], ignore_index=True).to_csv(DATA_FILE, index=False)
        else:
            df_new.to_csv(DATA_FILE, index=False)
        st.success("Data Saved! Go to the 'Bake List' tab.")

with tab2:
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%A")
    st.header(f"Bake List for {tomorrow_date}")
    
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Filter for the most recent entry
        latest_date = df['Date'].max()
        current_plan = df[df['Date'] == latest_date]
        
        # We need to show Every Day items + whatever belongs to Tomorrow's rotation
        tomorrow_rot = ROTATIONS.get(tomorrow_date, [])
        
        st.write("### 🥣 Production Items")
        for index, row in current_plan.iterrows():
            # Only show if it's an every day item OR in tomorrow's specific rotation
            if row['Item'] in EVERY_DAY or row['Item'] in tomorrow_rot:
                st.metric(label=row['Item'], value=f"Bake {int(row['Next_Bake'])} units")
    else:
        st.info("Complete the End of Day Entry first to generate tomorrow's list.")
