import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURATION ---
DATA_FILE = "bakery_data.csv"

# Products & Schedule (Same as before)
EVERY_DAY = ["Cinnamon Burst", "Honey Whole Wheat", "Dakota", "Cracked Light Wheat", "Beehive White", "Pumpkin Chip", "Chocolate Cherry", "Chocolate Chip", "Snickerdoodle", "Sugar Cookie", "Pumpkin", "Oatmeal Chip", "Double Chocolate", "Gluten Free", "Cinnamon Rolls"]
ROTATIONS = {
    "Monday": ["Spinach and Cheese", "Sourdough", "Strawberry Rolls", "Bread Pudding"],
    "Tuesday": ["Strawberries and Cream", "Cheddar Bacon Rolls", "Mazurka"],
    "Wednesday": ["Wheat Sourdough", "Strawberry Rolls", "Brownies", "Bread Pudding"],
    "Thursday": ["Strawberries and Cream", "Cheddar Bacon Rolls", "Mazurka"],
    "Friday": [],
    "Saturday": ["Garlic Sourdough"],
    "Sunday": []
}

# --- APP INTERFACE ---
st.title("🥖 Bakery Management Portal")

tab1, tab2 = st.tabs(["End of Day Entry", "Analytics Dashboard"])

with tab1:
    st.header("Daily Closeout")
    day_name = datetime.now().strftime("%A")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Revenue & Cash
    revenue = st.number_input("Total Daily Revenue ($)", min_value=0.0, step=0.01)
    surplus = st.number_input("Surplus Cash (Above $100.00)", min_value=0.0, step=0.01)
    
    if surplus > 0:
        st.warning(f"ACTION: Deposit ${surplus:.2f} to the bank.")

    # Inventory Entry
    st.subheader(f"Inventory for {day_name}")
    todays_menu = EVERY_DAY + ROTATIONS.get(day_name, [])
    
    daily_data = []
    for item in todays_menu:
        col1, col2, col3 = st.columns(3)
        with col1: t0 = st.number_input(f"{item} (Today)", min_value=0, key=f"{item}_t0")
        with col2: t1 = st.number_input(f"Yesterday's Left", min_value=0, key=f"{item}_t1")
        with col3: t2 = st.number_input(f"Discount (2-Day)", min_value=0, key=f"{item}_t2")
        daily_data.append({"Date": date_str, "Item": item, "T0": t0, "T1": t1, "T2": t2, "Revenue": revenue})

    if st.button("Submit Data to Ledger"):
        df_new = pd.DataFrame(daily_data)
        if os.path.exists(DATA_FILE):
            df_old = pd.read_csv(DATA_FILE)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
        df_final.to_csv(DATA_FILE, index=False)
        st.success("Data Saved Successfully!")

with tab2:
    st.header("Averages & Trends")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Monthly Revenue Average
        avg_rev = df.groupby(df['Date'].dt.strftime('%B'))['Revenue'].mean()
        st.write("### Average Monthly Revenue")
        st.bar_chart(avg_rev)
        
        # Most Wasted Items
        st.write("### Waste Analysis (Items Tossed)")
        waste_df = df.groupby('Item')['T2'].sum().sort_values(ascending=False)
        st.table(waste_df)
    else:
        st.info("No data recorded yet. Submit an entry to see trends.")
