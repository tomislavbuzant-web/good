import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# Fixed the CSS parameter error (unsafe_allow_html)
st.markdown("""
    <style>
    .main { background-color: #f1f3f5; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #2e7d32; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 5px 5px 0 0; 
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# File Management
FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns, initial_val=None):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(initial_val) if initial_val else pd.DataFrame(columns=columns)

def format_euro_date(date_str):
    try: return pd.to_datetime(date_str).strftime('%d.%m.%Y')
    except: return date_str

# --- 2. USDA-INSPIRED KETO DATA ---
USDA_KETO = {
    "Eggs (Large)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70},
    "Grass-fed Butter": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100},
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290},
    "Chicken Thigh (100g)": {"fat": 15, "prot": 20, "carb": 0, "cal": 210},
    "Avocado (Medium)": {"fat": 21, "prot": 3, "carb": 3, "cal": 240},
    "Coconut Oil (1tbsp)": {"fat": 14, "prot": 0, "carb": 0, "cal": 120},
    "Bacon (2 slices)": {"fat": 7, "prot": 6, "carb": 0, "cal": 90},
    "Salmon (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200},
    "Spinach (100g)": {"fat": 0.4, "prot": 2.9, "carb": 1.4, "cal": 23}
}

# --- 3. SIDEBAR ---
st.sidebar.title("🥑 Keto Pro Profile")
profile_pic = st.sidebar.file_uploader("Upload Profile Picture", type=['jpg', 'png'])
if profile_pic: st.sidebar.image(profile_pic, width=120)

user_full_name = st.sidebar.text_input("Name & Last Name", "User Name")
meas_pref = st.sidebar.selectbox("System", ["Metric (kg/cm)", "Imperial (lbs/ft)"])

# --- 4. TABS ---
tab_fast, tab_macro, tab_fridge, tab_profile = st.tabs([
    "🕒 Fasting Tracker", "🧮 Macro Calculator", "🥗 Fridge & Recipes", "👤 Profile & Export"
])

# --- TAB 1: FASTING ---
with tab_fast:
    st.header("Intermittent Fasting")
    if 'start_time' not in st.session_state: st.session_state.start_time = None

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Start Fast Clock"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ Finish & Log Fast"):
            if st.session_state.start_time:
                dur = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_f = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Hours": [round(dur, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_f]), FAST_FILE)
                st.session_state.start_time = None
                st.success("Fast Logged!")
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Time Elapsed", f"{elapsed:.2f} hrs")
        st.progress(min(elapsed/16, 1.0))

# --- TAB 2: MACRO CALCULATOR ---
with tab_macro:
    st.header("Keto Macro Engine")
    mc1, mc2 = st.columns(2)
    with mc1:
        age = st.number_input("Age", 18, 100, 35)
        weight = st.number_input("Weight (kg)", 40.0, 250.0, 90.0)
    with mc2:
        height = st.number_input("Height (cm)", 100, 250, 180)
        activity = st.selectbox("Activity", ["Sedentary", "Light", "Moderate", "High"])

    if st.button("Generate My Targets"):
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        mult = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "High": 1.725}[activity]
        tdee = bmr * mult
        
        # 70/25/5 Ratio
        st.session_state.tgt_f, st.session_state.tgt_p, st.session_state.tgt_c = (tdee*0.7)/9, (tdee*0.25)/4, (tdee*0.05)/4
        st.success(f"Goal: {int(tdee)} Calories")
        m1, m2, m3 = st.columns(3)
        m1.metric("Fat", f"{int(st.session_state.tgt_f)}g")
        m2.metric("Protein", f"{int(st.session_state.tgt_p)}g")
        m3.metric("Net Carbs", f"{int(st.session_state.tgt_c)}g")

# --- TAB 3: FRIDGE & RECIPES ---
with tab_fridge:
    st.header("Smart Fridge & Recipe Suggestions")
    
    fridge = st.multiselect("What is in your fridge?", list(USDA_KETO.keys()))
    
    if fridge:
        st.subheader("👨‍🍳 Tailored Portions")
        if 'tgt_p' in st.session_state:
            primary = fridge[0]
            # Grams needed to hit protein target
            needed_g = int((st.session_state.tgt_p / USDA_KETO[primary]['prot']) * 100)
            st.info(f"To hit your protein goal using **{primary}**, you should consume approximately **{needed_g}g** today.")
        
        st.subheader("🔗 Verified Recipe Sources")
        query = "+".join(fridge).replace(" ", "+")
        
        # Checked URLs for reliability
        st.markdown(f"✅ [DietDoctor Recipes](https://www.dietdoctor.com/low-carb/keto/recipes/search?s={query})")
        st.markdown(f"✅ [Wholesome Yum (High Accuracy)](https://www.wholesomeyum.com/?s={query})")
        st.markdown(f"✅ [AllRecipes Keto Filter](https://www.allrecipes.com/search?q={query}+keto)")
        st.markdown(f"✅ [Ruled.Me Recipe Index](https://www.ruled.me/?s={query})")
        st.markdown(f"🎥 [Headbanger's Kitchen (YouTube Search)](https://www.youtube.com/@HeadbangersKitchen/search?query={query})")

# --- TAB 4: PROFILE & EXPORT ---
with tab_profile:
    st.header(f"Profile: {user_full_name}")
    
    # Weight Entry
    w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"], {"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [90.0]})
    curr_w = st.number_input("Log New Weight (kg)", 30.0, 250.0, 90.0)
    if st.button("Save Weight Entry"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [curr_w]})
        save_data(pd.
