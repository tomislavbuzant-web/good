import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. PAGE CONFIGURATION ---
# Simple configuration without custom CSS to avoid Python 3.13 errors
st.set_page_config(page_title="Keto Pro", page_icon="🥑")

# Data storage file
DATA_FILE = "weight_history.csv"

def load_weight_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["Date", "Weight_kg"])
    return pd.DataFrame(columns=["Date", "Weight_kg"])

# --- 2. FASTING LOGIC (16/8) ---
st.title("🥑 Keto Pro Dashboard")

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

st.header("🕒 16/8 Fasting Timer")
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Start Fast"):
        st.session_state.start_time = datetime.datetime.now()
with c2:
    if st.button("🍽️ End Fast"):
        st.session_state.start_time = None

if st.session_state.start_time:
    now = datetime.datetime.now()
    elapsed = now - st.session_state.start_time
    hours_passed = elapsed.total_seconds() / 3600
    st.metric("Hours Elapsed", f"{hours_passed:.1f}h")
    
    progress_val = min(hours_passed / 16.0, 1.0)
    st.progress(progress_val)
    
    if hours_passed >= 16:
        st.success("Target Reached! You can eat now.")
    else:
        remaining = 16 - hours_passed
        st.write(f"Finish in: **{remaining:.1f} hours**")
else:
    st.info("Timer is off. Press Start after your last meal.")

st.divider()

# --- 3. SUPPLEMENTS CHECKLIST ---
st.header("💊 Daily Supplements")
# You can add or remove items from this list easily
supps = [
    "Magnesium (400mg) - Evening",
    "Potassium (1000mg) - With meals",
    "Omega-3 (2g) - With meals",
    "Vitamin D3 (5000 IU) - Morning",
    "MCT Oil (15ml) - In coffee/salad"
]

for s in supps:
    st.checkbox(s)

st.divider()

# --- 4. SMART KITCHEN & RECIPES ---
st.header("🍳 Fridge Recipe Finder")
inventory = st.text_input("What's in your fridge? (e.g., eggs, steak)").lower()

recipes = [
    {"name": "Keto Omelette", "items": ["eggs", "cheese", "butter"], "steps": "Fry 3 eggs in butter (approx 180°C), fold in cheese."},
    {"name": "Steak & Greens", "items": ["steak", "spinach", "butter"], "steps": "Sear steak, sauté spinach in butter."},
    {"name": "Avocado Salmon", "items": ["salmon", "avocado", "lemon"], "steps": "Bake salmon, serve with avocado."},
    {"name": "Bulletproof Coffee", "items": ["coffee", "mct oil", "butter"], "steps": "Blend coffee with MCT and butter."}
]

if inventory:
    found = False
    for r in recipes:
        if any(item in inventory for item in r['items']):
            with st.expander(f"📖 {r['name']}"):
                st.write(f"**Need:** {', '.join(r['items'])}")
                st.write(f"**Instructions:** {r['steps']}")
            found = True
    if not found:
        st.write("No direct match found.")

st.divider()

# --- 5. WEIGHT PROGRESS (METRIC) ---
st.header("⚖️ Weight Tracker (kg)")
current_w = st.number_input("Enter Weight (kg):", min_value=30.0, max_value=250.0, step=0.1)

if st.button("Log Weight Today"):
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    new_entry = pd.DataFrame({"Date": [today_str], "Weight_kg": [current_w]})
    df = load_weight_data()
    df = pd.concat([df, new_entry], ignore_index=True).drop_duplicates(subset=['Date'], keep='last')
    df.to_csv(DATA_FILE, index=False)
    st.success(f"Logged {current_w} kg")

df_display = load_weight_data()
if not df_display.empty:
    df_display['Date'] = pd.to_datetime(df_display['Date'])
    st.line_chart(df_display.set_index('Date'))
