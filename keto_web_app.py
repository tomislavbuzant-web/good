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

# --- 3. TABS ---
tab_fast, tab_macros, tab_food, tab_profile = st.tabs([
    "🕒 Fasting", "🧮 Macro & Meal Calc", "🥗 Food Library", "👤 Profile & Export"
])

# --- TAB 1: FASTING ---
with tab_fast:
    st.header("16/8 Fasting Tracker")
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
                st.rer
