import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# Custom CSS for a more "App-like" feel
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_base_html=True)

# Files
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

# --- 2. USDA-BASED KETO LIBRARY ---
# Using specific USDA FoodData Central mapped values
USDA_KETO = {
    "Eggs (Large)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70},
    "Grass-fed Butter": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100},
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290},
    "Chicken Thigh (100g)": {"fat": 15, "prot": 20, "carb": 0, "cal": 210},
    "Avocado (Medium)": {"fat": 21, "prot": 3, "carb": 3, "cal": 240},
    "Spinach (Raw 100g)": {"fat": 0.4, "prot": 2.9, "carb": 1.4, "cal": 23},
    "Coconut Oil (1tbsp)": {"fat": 14, "prot": 0, "carb": 0, "cal": 120},
    "Bacon (2 slices)": {"fat": 7, "prot": 6, "carb": 0, "cal": 90},
    "Salmon (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200}
}

# --- 3. SIDEBAR ---
st.sidebar.title("🥑 Keto Pro Profile")
profile_pic = st.sidebar.file_uploader("Upload Profile Picture", type=['jpg', 'png'])
if profile_pic: st.sidebar.image(profile_pic, width=120)

user_name = st.sidebar.text_input("First & Last Name", "User")
meas_system = st.sidebar.radio("Preferred Measurement", ["Metric (kg/cm)", "Imperial (lbs/ft)"])

# --- 4. TABS ---
tab_fast, tab_macro, tab_fridge, tab_profile = st.tabs([
    "🕒 Fasting", "🧮 Macro Calculator", "🛒 Food Library & Fridge", "👤 Profile & Export"
])

# --- TAB 1: FASTING ---
with tab_fast:
    st.header("Intermittent Fasting Tracker")
    c1, c2, c3 = st.columns([1,1,2])
    
    if 'start_time' not in st.session_state: st.session_state.start_time = None

    with c1:
        if st.button("🚀 Start Fast"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ End Fast"):
            if st.session_state.start_time:
                dur = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_f = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Hours": [round(dur, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_f]), FAST_FILE)
                st.session_state.start_time = None
                st.rerun()
    
    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Current Fast Duration", f"{elapsed:.2f} hrs")
        st.progress(min(elapsed/16, 1.0))

# --- TAB 2: MACRO CALCULATOR ---
with tab_macro:
    st.header("Personalized Keto Targets")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 18, 100, 35)
        weight = st.number_input("Weight (kg)", 40.0, 250.0, 90.0)
    with col2:
        height = st.number_input("Height (cm)", 100, 250, 180)
        activity = st.select_slider("Lifestyle", options=["Sedentary", "Light", "Moderate", "Very Active"])

    if st.button("Calculate My Macros"):
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        act_mult = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Very Active": 1.725}
        tdee = bmr * act_mult[activity]
        
        # 70/25/5 Keto Split
        f_g, p_g, c_g = (tdee*0.7)/9, (tdee*0.25)/4, (tdee*0.05)/4
        st.session_state.targets = {"fat": f_g, "prot": p_g, "carb": c_g, "cal": tdee}
        
        st.subheader(f"Your Daily Goal: {int(tdee)} kcal")
        m1, m2, m3 = st.columns(3)
        m1.metric("Fat", f"{int(f_g)}g")
        m2.metric("Protein", f"{int(p_g)}g")
        m3.metric("Net Carbs", f"{int(c_g)}g")

# --- TAB 3: FOOD LIBRARY & FRIDGE ---
with tab_fridge:
    st.header("Fridge Inventory & Recipe Engine")
    st.write("Select ingredients you have to generate a custom meal plan.")
    
    fridge_items = st.multiselect("What's in your fridge?", list(USDA_KETO.keys()))
    
    if fridge_items:
        st.divider()
        st.subheader("🍳 Suggested Daily Meal Plan")
        
        # Logic to fulfill macros based on fridge items
        if 'targets' in st.session_state:
            t = st.session_state.targets
            st.info(f"Based on your **{int(t['prot'])}g Protein** goal, here is your intake for today:")
            
            main_prot = fridge_items[0]
            amt = int((t['prot'] / USDA_KETO[main_prot]['prot']) * 100)
            
            st.write(f"1. **Main Meal:** Eat **{amt}g of {main_prot}**.")
            st.write(f"2. **Fat Adjustment:** Add **{int((t['fat'] - (amt*USDA_KETO[main_prot]['fat']/100))/12)} tbsp** of Butter/Oil.")
        
        st.subheader("📖 Top Verified Keto Recipes")
        search_term = "+".join(fridge_items).replace(" ", "+")
        
        # Manually verified high-quality Keto sources
        recipes = [
            {"name": "DietDoctor - Keto Recipes", "url": f"https://www.dietdoctor.com/low-carb/keto/recipes/search?s={search_term}"},
            {"name": "AllRecipes - Keto Collection", "url": "https://www.allrecipes.com/recipes/22934/healthy-recipes/keto-diet/"},
            {"name": "Wholesome Yum - 10-Min Meals", "url": "https://www.wholesomeyum.com/recipe-index/"},
            {"name": "Ruled.me - Video Guides", "url": "https://www.ruled.me/keto-recipes/"},
            {"name": "Headbanger's Kitchen (Video)", "url": "https://www.youtube.com/@HeadbangersKitchen/search?query=keto"}
        ]
        
        for r in recipes:
            st.markdown(f"🔗 [{r['name']}]({r['url']})")

# --- TAB 4: PROFILE & EXPORT ---
with tab_profile:
    st.header("Historical Overview")
    
    # Weight History
    w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"], {"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [90.0]})
    
    log_w = st.number_input("Update Current Weight (kg)", 30.0, 250.0, 90.0)
    if st.button("Log Weight"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [log_w]})
        save_data(pd.concat([w_df, new_w]), WEIGHT_FILE)
        st.rerun()

    st.line_chart(w_df.set_index("Date"))
    
    st.divider()
    st.subheader("📂 Export Data Center")
    col_ex1, col_ex2 = st.columns(2)
    
    # Fasting Export
    f_hist = load_data(FAST_FILE, ["Date", "Hours"])
    if not f_hist.empty:
        f_exp = f_hist.copy()
        f_exp['Date'] = f_exp['Date'].apply(format_euro_date)
        col_ex1.download_button("📥 Fasting CSV", f_exp.to_csv(index=False), "fasting.csv", "text/csv")
        col_ex1.download_button("📥 Fasting TXT", f_exp.to_string(index=False), "fasting.txt", "text/plain")

    # Weight Export
    if not w_df.empty:
        w_exp = w_df.copy()
        w_exp['Date'] = w_exp['Date'].apply(format_euro_date)
        col_ex2.download_button("📥 Weight CSV", w_exp.to_csv(index=False), "weight.csv", "text/csv")
        col_ex2.download_button("📥 Weight TXT", w_exp.to_string(index=False), "weight.txt", "text/plain")
