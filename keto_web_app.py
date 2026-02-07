import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f1f3f5; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #2e7d32; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 8px 8px 0 0; 
        padding: 10px 15px;
        border: 1px solid #ddd;
    }
    .stButton>button { border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# File Management
FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns, initial_val=None):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame(columns=columns)
    if initial_val:
        return pd.DataFrame(initial_val)
    return pd.DataFrame(columns=columns)

def format_euro_date(date_str):
    try:
        return pd.to_datetime(date_str).strftime('%d.%m.%Y')
    except:
        return date_str

# --- 2. KETO FOOD DATABASE (USDA-BASED) ---
# Fixed the unterminated string literal error here
USDA_KETO = {
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290},
    "Eggs (Large)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70},
    "Grass-fed Butter (15g)": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100},
    "Salmon (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200},
    "Avocado (Medium)": {"fat": 21, "prot": 3, "carb": 3, "cal": 240},
    "Chicken Thigh (100g)": {"fat": 15, "prot": 20, "carb": 0, "cal": 210},
    "Coconut Oil (1tbsp)": {"fat": 14, "prot": 0, "carb": 0, "cal": 120},
    "Bacon (2 slices)": {"fat": 7, "prot": 6, "carb": 0, "cal": 90},
    "Spinach (100g)": {"fat": 0.4, "prot": 2.9, "carb": 1.4, "cal": 23},
    "Pecans (30g)": {"fat": 20, "prot": 3, "carb": 1.2, "cal": 200}
}

# --- 3. SIDEBAR ---
st.sidebar.title("🥑 Keto Pro Profile")
profile_pic = st.sidebar.file_uploader("Upload Photo", type=['jpg', 'png'])
if profile_pic:
    st.sidebar.image(profile_pic, width=120)

user_full_name = st.sidebar.text_input("Name & Last Name", "User Name")
st.sidebar.info("System: Metric (kg/cm) & Celsius")

# --- 4. TABS ---
tab_fast, tab_macro, tab_fridge, tab_profile = st.tabs([
    "🕒 Fasting Tracker", "🧮 Macro Calculator", "🥗 Food Library & Fridge", "👤 Profile & Export"
])

# --- TAB 1: FASTING ---
with tab_fast:
    st.header("16/8 Fasting Clock")
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Start Fasting Now"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ End Fast & Log"):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_entry = pd.DataFrame({
                    "Date": [datetime.date.today().strftime('%Y-%m-%d')], 
                    "Hours": [round(duration, 2)]
                })
                history = load_data(FAST_FILE, ["Date", "Hours"])
                save_data(pd.concat([history, new_entry], ignore_index=True), FAST_FILE)
                st.session_state.start_time = None
                st.success(f"Logged {duration:.2f} hours!")
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Time Elapsed", f"{elapsed:.2f} hrs")
        st.progress(min(elapsed/16, 1.0))

# --- TAB 2: MACRO CALCULATOR ---
with tab_macro:
    st.header("Personalized Keto Calculator")
    mc1, mc2 = st.columns(2)
    with mc1:
        age = st.number_input("Age (Years)", 18, 100, 35)
        weight_kg = st.number_input("Current Weight (kg)", 40.0, 250.0, 90.0)
    with mc2:
        height_cm = st.number_input("Height (cm)", 100, 250, 180)
        activity_lvl = st.selectbox("Daily Activity", ["Sedentary", "Light", "Moderate", "High"])

    if st.button("Calculate Daily Targets"):
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        activity_map = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "High": 1.725}
        tdee = bmr * activity_map[activity_lvl]
        
        st.session_state.f_goal = (tdee * 0.70) / 9
        st.session_state.p_goal = (tdee * 0.25) / 4
        st.session_state.c_goal = (tdee * 0.05) / 4
        st.session_state.tdee = tdee
        
        st.success(f"Daily Target: {int(tdee)} Calories")
        m1, m2, m3 = st.columns(3)
        m1.metric("Fat Goal", f"{int(st.session_state.f_goal)}g")
        m2.metric("Protein Goal", f"{int(st.session_state.p_goal)}g")
        m3.metric("Net Carb Limit", f"{int(st.session_state.c_goal)}g")

# --- TAB 3: FOOD LIBRARY & FRIDGE ---
with tab_fridge:
    st.header("Smart Fridge & Recipe Engine")
    
    st.subheader("1. Select ingredients from your fridge:")
    items_in_fridge = st.multiselect("Available Items:", list(USDA_KETO.keys()))
    
    if items_in_fridge:
        st.divider()
        st.subheader("👨‍🍳 Recommended Portions to Hit Macros")
        
        if 'p_goal' in st.session_state:
            primary_food = items_in_fridge[0]
            prot_per_100 = USDA_KETO[primary_food]['prot']
            if prot_per_100 > 0:
                needed_grams = int((st.session_state.p_goal / prot_per_100) * 100)
                st.info(f"To hit your protein goal with **{primary_food}**, you should consume **{needed_grams}g** today.")
                
                fat_in_food = (needed_grams / 100) * USDA_KETO[primary_food]['fat']
                remaining_fat = st.session_state.f_goal - fat_in_food
                butter_tbsp = max(0, int(remaining_fat / 12))
                st.write(f"➡️ Add **{butter_tbsp} tbsp** of Butter or Coconut oil to hit your fat target.")
        else:
            st.warning("Please calculate your macros in the 'Macro Calculator' tab first!")

        st.subheader("🔍 Verified Keto Recipes")
        search_query = "+".join(items_in_fridge).replace(" ", "+")
        
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"📖 [DietDoctor Recipes](https://www.dietdoctor.com/low-carb/keto/recipes/search?s={search_query})")
            st.markdown(f"📖 [Wholesome Yum Meals](https://www.wholesomeyum.com/?s={search_query})")
        with r2:
            st.markdown(f"📖 [AllRecipes Keto](https://www.allrecipes.com/search?q={search_query}+keto)")
            st.markdown(f"🎥 [Headbanger's Kitchen (YouTube)](https://www.youtube.com/@HeadbangersKitchen/search?query={search_query})")

# --- TAB 4: PROFILE & EXPORT ---
with tab_profile:
    st.header(f"Health Data: {user_full_name}")
    
    weight_hist = load_data(WEIGHT_FILE, ["Date", "Weight_kg"], {"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [90.0]})
    
    new_w = st.number_input("Log Current Weight (kg)", 30.0, 250.0, 90.0)
    if st.button("Save Weight Log"):
        w_entry = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [new_w]})
        save_data(pd.concat([weight_hist, w_entry], ignore_index=True), WEIGHT_FILE)
        st.rerun()

    if not weight_hist.empty:
        st.subheader("Weight Trend")
        w_plot = weight_hist.copy()
        w_plot['Date'] = pd.to_datetime(w_plot['Date'])
        st.line_chart(w_plot.set_index('Date'))

    st.divider()
    st.subheader("📂 Export Data (Metric/Euro)")
    col_ex1, col_ex2 = st.columns(2)
    
    f_hist = load_data(FAST_FILE, ["Date", "Hours"])
    if not f_hist.empty:
        f_exp = f_hist.copy()
        f_exp['Date'] = f_exp['Date'].apply(format_euro_date)
        col_ex1.download_button("📥 Fasting History (CSV)", f_exp.to_csv(index=False), "fasting_history.csv", "text/csv")
        
    if not weight_hist.empty:
        w_exp = weight_hist.copy()
        w_exp['Date'] = w_exp['Date'].apply(format_euro_date)
        col_ex2.download_button("📥 Weight History (CSV)", w_exp.to_csv(index=False), "weight_history.csv", "text/csv")
