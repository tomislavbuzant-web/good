import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Keto Pro Mobile", page_icon="🥑", layout="centered")

# Basic styling to make it look like a mobile app
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2e7d32; color: white; }
    .stProgress > div > div > div > div { background-color: #2e7d32; }
</style>
""", unsafe_allow_input=True)

# Data storage file name
DATA_FILE = "weight_history.csv"

def load_weight_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Weight_kg"])

# --- 2. FASTING LOGIC (16/8) ---
st.title("🥑 Keto Pro Dashboard")

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

st.subheader("🕒 16/8 Fasting Timer")
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Start Fast"):
        st.session_state.start_time = datetime.datetime.now()
with c2:
    if st.button("🍽️ End Fast"):
        st.session_state.start_time = None

if st.session_state.start_time:
    elapsed = datetime.datetime.now() - st.session_state.start_time
    hours_passed = elapsed.total_seconds() / 3600
    st.metric("Hours Elapsed", f"{hours_passed:.1f}h")
    
    progress = min(hours_passed / 16.0, 1.0)
    st.progress(progress)
    
    if hours_passed >= 16:
        st.success("Target Reached! You can eat now.")
    else:
        remaining = 16 - hours_passed
        st.write(f"Finish in: **{remaining:.1f} hours**")
else:
    st.info("Timer is off. Press Start after your last meal.")

st.divider()

# --- 3. SUPPLEMENTS CHECKLIST ---
st.subheader("💊 Daily Supplement Stack")
supps = {
    "Magnesium (400mg)": "Evening - for sleep and cramps",
    "Potassium (1000mg)": "With meals - for electrolytes",
    "Omega-3 (2g)": "With fat-containing meal",
    "Vitamin D3 (5000 IU)": "Morning",
    "MCT Oil (15ml)": "In coffee or salad"
}

for name, note in supps.items():
    st.checkbox(f"{name} ({note})")

st.divider()

# --- 4. SMART KITCHEN & RECIPES ---
st.subheader("🍳 Fridge Recipe Finder")
inventory = st.text_input("What's in your fridge? (e.g., eggs, steak, spinach)").lower()

# Recipe Database
recipes = [
    {"name": "Keto Omelette", "items": ["eggs", "cheese", "butter"], "steps": "Fry 3 eggs in butter (200°C), fold in cheese."},
    {"name": "Steak & Greens", "items": ["steak", "spinach", "butter"], "steps": "Sear steak, sauté spinach in the pan with butter."},
    {"name": "Avocado Salmon", "items": ["salmon", "avocado", "lemon"], "steps": "Bake salmon, serve with fresh avocado slices and lemon."},
    {"name": "Bulletproof Coffee", "items": ["coffee", "mct oil", "butter"], "steps": "Blend hot coffee with 15ml MCT and 10g butter."}
]

if inventory:
    matches = [r for r in recipes if any(item in inventory for item in r['items'])]
    if matches:
        for m in matches:
            with st.expander(f"📖 {m['name']}"):
                st.write(f"**Need:** {', '.join(m['items'])}")
                st.write(f"**Instructions:** {m['steps']}")
    else:
        st.write("No exact matches. Try a simple protein + healthy fat!")

st.divider()

# --- 5. WEIGHT PROGRESS (METRIC) ---
st.subheader("⚖️ Weight Tracker (kg)")
current_w = st.number_input("Enter Weight (kg):", min_value=30.0, max_value=200.0, value=80.0, step=0.1)

if st.button("Log Weight Today"):
    new_entry = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [current_w]})
    df = load_weight_data()
    df = pd.concat([df, new_entry], ignore_index=True).drop_duplicates(subset=['Date'], keep='last')
    df.to_csv(DATA_FILE, index=False)
    st.toast("Weight saved!")

# Display chart if data exists
df_display = load_weight_data()
if not df_display.empty:
    df_display['Date'] = pd.to_datetime(df_display['Date'])
    st.line_chart(df_display.set_index('Date'))
