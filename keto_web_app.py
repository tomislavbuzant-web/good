import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

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

# --- 2. SIDEBAR PROFILE ---
st.sidebar.title("👤 User Profile")
profile_pic = st.sidebar.file_uploader("Upload Photo", type=['jpg', 'png'])
if profile_pic:
    st.sidebar.image(profile_pic, width=100)

user_name = st.sidebar.text_input("Name", "User")
meas_system = st.sidebar.radio("Measurement System", ["Metric (kg/cm)", "Imperial (lbs/ft)"], index=0)

# --- 3. TABS (RESTRUCTURED FOR STABILITY) ---
tab_fast, tab_macros, tab_food, tab_profile = st.tabs([
    "🕒 Fasting Tracker", "🧮 Macro & Meal Calc", "🥗 Food Library", "👤 Profile & Export"
])

# --- TAB 1: FASTING ---
with tab_fast:
    st.header("16/8 Fasting & Hydration")
    
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Start Fasting"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ Log & End Fast"):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_fast = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Hours": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_fast]), FAST_FILE)
                st.session_state.start_time = None
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Time Fasted", f"{elapsed:.2f} hrs")
        st.progress(min(elapsed/16, 1.0))
    
    st.divider()
    st.subheader("💧 Hydration Tracker")
    water_liters = st.slider("Liters of Water Today", 0.0, 5.0, 2.0, 0.25)
    st.write(f"Goal: 3.0L | Progress: {water_liters}L")

# --- TAB 2: MACRO & MEAL CALCULATOR ---
with tab_macros:
    st.header("Keto Blueprint")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        age = st.number_input("Age (Years)", 18, 100, 35)
        weight = st.number_input("Current Weight (kg)", 40.0, 250.0, 90.0)
    with m_col2:
        height = st.number_input("Height (cm)", 100, 250, 180)
        activity = st.selectbox("Activity Level", ["Sedentary", "Light", "Moderate", "Active"])

    if st.button("Calculate Daily Plan"):
        # BMR Math
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        tdee = bmr * {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725}[activity]
        
        fat_g = (tdee * 0.70) / 9
        prot_g = (tdee * 0.25) / 4
        carb_g = (tdee * 0.05) / 4
        
        st.success(f"Target: {int(tdee)} kcal | {int(fat_g)}g Fat | {int(prot_g)}g Protein | {int(carb_g)}g Carbs")
        
        # Suggested Meal portions
        st.subheader("🍳 Suggested Daily Ingredients")
        steak = int(prot_g / 0.24) # 24g protein per 100g ribeye
        fat_from_steak = steak * 0.22 / 100
        remaining_fat = fat_g - fat_from_steak
        butter = int(remaining_fat / 12) # 12g fat per tbsp

        st.info(f"""
        - **{steak}g Fatty Beef/Ribeye:** Fulfills your protein.
        - **{butter} tbsp Butter/Coconut Oil:** Added to coffee or cooking.
        - **1-2 Avocados:** For healthy fats and potassium.
        - **Handful of Pecans/Walnuts:** For snacks.
        """)

# --- TAB 3: FOOD LIBRARY ---
with tab_food:
    st.header("Keto Staples Reference")
    st.write("Average macros per 100g:")
    st.table(pd.DataFrame({
        "Food": ["Ribeye", "Salmon", "Avocado", "Butter", "Eggs", "Spinach"],
        "Fat (g)": [22, 13, 15, 81, 11, 0.4],
        "Protein (g)": [24, 20, 2, 0.9, 13, 2.9],
        "Net Carbs (g)": [0, 0, 2, 0, 1.1, 1.4]
    }))

# --- TAB 4: PROFILE & EXPORT ---
with tab_profile:
    st.header(f"Profile: {user_name}")
    
    # Weight Progress Table & Graph
    hist_w = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not hist_w.empty:
        st.subheader("Weight Trend")
        plot_df = hist_w.copy()
        plot_df['Date'] = pd.to_datetime(plot_df['Date'])
        st.line_chart(plot_df.set_index('Date'))
        
        st.subheader("Log History")
        disp_df = hist_w.copy()
        disp_df['Date'] = disp_df['Date'].apply(format_euro_date)
        st.dataframe(disp_df, use_container_width=True)

    # Export Center
    st.divider()
    st.subheader("📂 Export Center")
    if not hist_w.empty:
        exp_df = hist_w.copy()
        exp_df['Date'] = exp_df['Date'].apply(format_euro_date)
        st.download_button("📥 Download Weight History (CSV)", exp_df.to_csv(index=False), "weight.csv", "text/csv")
    
    hist_f = load_data(FAST_FILE, ["Date", "Hours"])
    if not hist_f.empty:
        exp_f = hist_f.copy()
        exp_f['Date'] = exp_f['Date'].apply(format_euro_date)
        st.download_button("📥 Download Fasting History (CSV)", exp_f.to_csv(index=False), "fasting.csv", "text/csv")
