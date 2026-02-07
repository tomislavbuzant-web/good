import streamlit as st
import datetime

# --- SETTINGS ---
st.set_page_config(page_title="My Keto Pro", page_icon="🥑")

# Custom Styling for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_input=True)

st.title("🥑 My Keto Pro Dashboard")

# --- 1. INTERMITTENT FASTING (16/8) ---
st.header("🕒 Fasting Tracker")
col1, col2 = st.columns(2)

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

with col1:
    if st.button("🏁 Start 16h Fast"):
        st.session_state.start_time = datetime.datetime.now()
with col2:
    if st.button("🍽️ End Fast"):
        st.session_state.start_time = None

if st.session_state.start_time:
    now = datetime.datetime.now()
    elapsed = now - st.session_state.start_time
    hours_passed = elapsed.total_seconds() / 3600
    remaining = max(0, 16 - hours_passed)
    
    st.metric("Hours Fasted", f"{hours_passed:.1f}h")
    
    if hours_passed < 16:
        st.write(f"Keep going! You have **{remaining:.1f} hours** left.")
        st.progress(hours_passed / 16)
    else:
        st.success("✅ 16-hour window complete! You can now eat.")
else:
    st.info("Log your last meal to start the timer.")

# --- 2. DETAILED SUPPLEMENT PLAN ---
st.header("💊 My Supplement Stack")
st.write("Metric doses for your Keto regimen:")

# Using columns for a checklist
c1, c2 = st.columns(2)
with c1:
    st.checkbox("Magnesium (400mg) - Evening")
    st.checkbox("Potassium (1000mg) - With food")
    st.checkbox("Omega-3 (2g) - Morning")
with c2:
    st.checkbox("Vitamin D3 (5000 IU)")
    st.checkbox("MCT Oil (15ml) - In Coffee")
    st.checkbox("Electrolyte Powder - In 1L Water")

# --- 3. SMART KITCHEN (Fridge Search) ---
st.header("🍳 What's in the Fridge?")
user_ingredients = st.text_input("Type ingredients you have (e.g. eggs, spinach, steak)").lower()

# Detailed Recipe Database
recipes = [
    {"name": "Keto Steak & Greens", "items": ["steak", "spinach", "butter"], "steps": "Sear steak in butter. Sauté spinach in the leftover fat."},
    {"name": "Creamy Avocado Eggs", "items": ["eggs", "avocado", "cheese"], "steps": "Scramble eggs with cheese. Serve inside a halved avocado."},
    {"name": "Salmon Bake", "items": ["salmon", "broccoli", "olive oil"], "steps": "Bake salmon and broccoli at 200°C for 15 mins with olive oil."},
    {"name": "Keto Coffee", "items": ["coffee", "mct oil", "butter"], "steps": "Blend all ingredients until frothy. Great for fasting mornings!"}
]

if user_ingredients:
    found_any = False
    for r in recipes:
        # Check if any user ingredient matches any recipe ingredient
        if any(ing in user_ingredients for ing in r['items']):
            with st.expander(f"📖 Suggestion: {r['name']}"):
                st.write(f"**Requires:** {', '.join(r['items'])}")
                st.write(f"**Instructions:** {r['steps']}")
            found_any = True
    if not found_any:
        st.write("No specific recipe match. Stick to: 1 Protein + 1 Green + 1 Healthy Fat!")

# --- 4. WEIGHT TRACKER (METRIC) ---
st.header("⚖️ Progress")
weight_kg = st.number_input("Current Weight (kg)", min_value=40.0, max_value=200.0, step=0.1)
if st.button("Log Daily Weight"):
    st.toast(f"Logged {weight_kg} kg! (Note: Data resets on refresh without a database)")
