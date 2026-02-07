import streamlit as st
import datetime
import pandas as pd
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Keto & Fasting Companion", layout="centered")

# Helper to save/load data in a simple way
DATA_FILE = "keto_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Weight_kg"])

# --- UI HEADER ---
st.title("🥑 Keto & Fasting Dashboard")
st.write(f"Today's Date: {datetime.date.today().strftime('%d %B %Y')}")

# --- SECTION 1: 16/8 FASTING ---
st.header("🕒 16/8 Intermittent Fasting")
if 'fast_start' not in st.session_state:
    st.session_state.fast_start = None

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Start Fasting Now"):
        st.session_state.fast_start = datetime.datetime.now()

with col2:
    if st.button("🍽️ End Fasting"):
        st.session_state.fast_start = None

if st.session_state.fast_start:
    elapsed = datetime.datetime.now() - st.session_state.fast_start
    hours = elapsed.total_seconds() / 3600
    st.info(f"Fasting for: **{hours:.1f} hours**")
    
    # Progress Bar
    progress = min(hours / 16.0, 1.0)
    st.progress(progress)
    if hours >= 16:
        st.success("Target reached! You can now eat.")
else:
    st.warning("Not currently fasting.")

# --- SECTION 2: WEIGHT TRACKER ---
st.header("⚖️ Weight Tracker (Metric)")
weight = st.number_input("Enter Weight (kg):", min_value=30.0, max_value=250.0, step=0.1)
if st.button("Log Weight"):
    new_data = pd.DataFrame({"Date": [datetime.date.today()], "Weight_kg": [weight]})
    df = load_data()
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"Saved: {weight} kg")

# Display Weight Chart
df = load_data()
if not df.empty:
    st.line_chart(df.set_index("Date"))

# --- SECTION 3: SUPPLEMENT CHECKLIST ---
st.header("💊 Daily Supplements")
supps = ["Magnesium", "Potassium", "Omega-3", "Vitamin D3", "MCT Oil"]
for s in supps:
    st.checkbox(s)

# --- SECTION 4: KITCHEN RECIPE FINDER ---
st.header("🍳 Fridge Recipe Finder")
fridge = st.text_input("What is in your fridge? (e.g., eggs, bacon, avocado)").lower()

recipes = {
    "Keto Omelette": ["eggs", "cheese", "butter"],
    "Bacon & Eggs": ["bacon", "eggs"],
    "Avocado Bowl": ["avocado", "tuna", "mayo"],
    "Steak": ["beef", "butter"]
}

if fridge:
    found = False
    for name, ingredients in recipes.items():
        if any(item in fridge for item in ingredients):
            st.write(f"✅ **You can make: {name}**")
            st.caption(f"Requires: {', '.join(ingredients)}")
            found = True
    if not found:
        st.write("No exact match, but try a protein + healthy fat!")