import streamlit as st
import datetime
import pandas as pd
import os
import io

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# Persistent Data Files
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

# --- 2. APP INTERFACE ---
st.sidebar.title("👤 User Profile")
profile_pic = st.sidebar.file_uploader("Upload Profile Picture", type=['jpg', 'png'])
if profile_pic:
    st.sidebar.image(profile_pic, width=100)

user_name = st.sidebar.text_input("Name", "User")
meas_system = st.sidebar.radio("Measurement System", ["Metric (kg/cm)", "Imperial (lbs/ft)"])

tab_fast, tab_macros, tab_food, tab_supps, tab_profile = st.tabs([
    "🕒 Fasting", "🧮 Macro Calc", "🥗 Food & Recipes", "💊 Supplements", "👤 Profile & Export"
])

# --- TAB 1: FASTING ---
with tab_fast:
    st.header("Intermittent Fasting Tracker")
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Start Fast"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ End Fast"):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_fast = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Hours": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_fast]), FAST_FILE)
                st.session_state.start_time = None
                st.success(f"Logged {duration:.1f} hours!")
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Elapsed Time", f"{elapsed:.2f} hrs")
        
        # Metabolic Stages
        if elapsed < 12: stage, color = "Glucose Burning", "blue"
        elif elapsed < 16: stage, color = "Transition to Ketosis", "orange"
        else: stage, color = "Autophagy & Fat Burning", "green"
        st.info(f"**Current Metabolic State:** {stage}")
        st.progress(min(elapsed/16, 1.0))

    

# --- TAB 2: MACRO CALCULATOR ---
with tab_macros:
    st.header("Keto Macro Calculator")
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age", 18, 100, 30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        weight = st.number_input(f"Weight ({'kg' if meas_system.startswith('Metric') else 'lbs'})", 40.0, 200.0, 90.0)
    with col_b:
        height = st.number_input(f"Height ({'cm' if meas_system.startswith('Metric') else 'in'})", 100, 250, 175)
        activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])

    if st.button("Calculate My Keto Macros"):
        # Basic BMR calculation (Mifflin-St Jeor)
        w_kg = weight if meas_system.startswith('Metric') else weight * 0.453592
        h_cm = height if meas_system.startswith('Metric') else height * 2.54
        bmr = (10 * w_kg) + (6.25 * h_cm) - (5 * age) + (5 if gender == "Male" else -161)
        
        # TDEE Multiplier
        mult = {"Sedentary": 1.2, "Lightly Active": 1.375, "Moderately Active": 1.55, "Very Active": 1.725}
        tdee = bmr * mult[activity]
        
        # Keto Ratios: 5% Carb, 25% Protein, 70% Fat
        st.success(f"Estimated Daily Calories: {int(tdee)} kcal")
        c1, c2, c3 = st.columns(3)
        c1.metric("Net Carbs", f"{int((tdee * 0.05) / 4)}g")
        c2.metric("Protein", f"{int((tdee * 0.25) / 4)}g")
        c3.metric("Fat", f"{int((tdee * 0.70) / 9)}g")

# --- TAB 5: PROFILE & EXPORT ---
with tab_profile:
    st.header(f"Profile: {user_name}")
    
    # Weight Entry
    curr_w = st.number_input("Update Weight (kg)", 30.0, 300.0, 90.0)
    if st.button("Log Weight Entry"):
        w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"], initial_val={"Date": ["2026-02-01"], "Weight_kg": [90.0]})
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [curr_w]})
        save_data(pd.concat([w_df, new_w]), WEIGHT_FILE)
    
    # Combined History Table
    st.subheader("Weight Loss & Fasting History")
    w_history = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_history.empty:
        w_history['Date'] = w_history['Date'].apply(format_euro_date)
        st.table(w_history.tail(5))
        
    # EXPORT SECTION
    st.divider()
    st.subheader("📂 Export Data")
    
    f_df = load_data(FAST_FILE, ["Date", "Hours"])
    if not f_df.empty:
        f_exp = f_df.copy()
        f_exp['Date'] = f_exp['Date'].apply(format_euro_date)
        st.download_button("📥 Export Fasting (CSV)", f_exp.to_csv(index=False), "fasting_history.csv", "text/csv")
        st.download_button("📥 Export Fasting (TXT)", f_exp.to_string(index=False), "fasting_history.txt", "text/plain")
    
    if not w_history.empty:
        st.download_button("📥 Export Weight (CSV)", w_history.to_csv(index=False), "weight_history.csv", "text/csv")
