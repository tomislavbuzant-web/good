import streamlit as st
import datetime
import pandas as pd
import os
import io

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# Formatting helper for European Dates (DD.MM.YYYY)
def format_euro_date(date_str):
    try:
        return pd.to_datetime(date_str).strftime('%d.%m.%Y')
    except:
        return date_str

# --- 2. LIBRARIES ---
KETO_FOODS = {
    "Avocado": {"Fat": 15, "NetCarb": 2, "Protein": 2},
    "Chicken Thigh": {"Fat": 15, "NetCarb": 0, "Protein": 20},
    "Spinach": {"Fat": 0, "NetCarb": 1, "Protein": 3},
    "Ribeye Steak": {"Fat": 22, "NetCarb": 0, "Protein": 24},
    "Salmon": {"Fat": 13, "NetCarb": 0, "Protein": 20},
    "Eggs": {"Fat": 5, "NetCarb": 0.6, "Protein": 6},
    "Butter": {"Fat": 12, "NetCarb": 0, "Protein": 0},
    "Bacon": {"Fat": 42, "NetCarb": 1.4, "Protein": 37}
}

# --- 3. APP INTERFACE ---
st.title("🥑 Keto Intelligence Pro")

tab1, tab2, tab3, tab4 = st.tabs(["🕒 Fasting Tracker", "🥗 Food & Recipes", "💊 Supplements", "📈 Progress & Export"])

# --- TAB 1: IMPROVED FASTING ---
with tab1:
    st.header("16/8 Intermittent Fasting")
    
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Fasting Clock"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with col2:
        if st.button("🍽️ Finish & Log Fast"):
            if st.session_state.start_time:
                end_time = datetime.datetime.now()
                duration = (end_time - st.session_state.start_time).total_seconds() / 3600
                date_str = end_time.strftime('%Y-%m-%d')
                new_fast = pd.DataFrame({"Date": [date_str], "Hours": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_fast]), FAST_FILE)
                st.session_state.start_time = None
                st.success(f"Logged {duration:.1f} hours!")
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        
        status = "⌛ Blood Sugar Dropping"
        if 12 <= elapsed < 16:
            status = "🔥 Ketosis Stage"
        elif elapsed >= 16:
            status = "🧬 Autophagy Initiated"
            
        st.subheader(f"Status: {status}")
        st.metric("Time Fasted", f"{elapsed:.2f} hrs")
        
        target = 16.0
        st.progress(min(elapsed / target, 1.0))
        
        if elapsed < target:
            st.write(f"Finish in: **{(target - elapsed):.2f} hours**")
        else:
            st.success("Target Reached!")

    

    st.divider()
    st.subheader("📜 Fasting History")
    f_df = load_data(FAST_FILE, ["Date", "Hours"])
    if not f_df.empty:
        f_df_display = f_df.copy()
        f_df_display['Date'] = f_df_display['Date'].apply(format_euro_date)
        st.table(f_df_display.tail(7))

# --- TAB 2: FOOD & RECIPES ---
with tab2:
    st.header("Keto Food Library")
    search_food = st.multiselect("In your fridge:", list(KETO_FOODS.keys()))
    if search_food:
        for f in search_food:
            m = KETO_FOODS[f]
            st.caption(f"**{f}**: {m['Fat']}g Fat | {m['NetCarb']}g Carbs | {m['Protein']}g Protein")

# --- TAB 3: SUPPLEMENTS ---
with tab3:
    st.header("Keto Supplement Stack")
    st.info("Tip: Take electrolytes during your fast and fat-soluble vitamins (D, K, Omega-3) with your first meal.")
    st.checkbox("Magnesium (Evening - 400mg)")
    st.checkbox("Potassium (With Meal - 1000mg)")
    st.checkbox("Sea Salt (During Fast - 2g)")

# --- TAB 4: PROGRESS & EXPORT ---
with tab4:
    st.header("Weight Progress (kg)")
    w_val = st.number_input("Log Weight Today", min_value=30.0, step=0.1)
    if st.button("Save Weight"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [w_val]})
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), new_w]), WEIGHT_FILE)
    
    w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_df.empty:
        w_df_chart = w_df.copy()
        w_df_chart['Date'] = pd.to_datetime(w_df_chart['Date'])
        st.line_chart(w_df_chart.set_index("Date"))

    st.divider()
    st.header("📂 Export Center")
    st.write("Download your data in European format (DD.MM.YYYY):")
    
    c_a, c_b = st.columns(2)
    
    if not f_df.empty:
        f_exp = f_df.copy()
        f_exp['Date'] = f_exp['Date'].apply(format_euro_date)
        f_csv = f_exp.to_csv(index=False).encode('utf-8')
        c_a.download_button("📥 Fasting History (CSV)", f_csv, "fasting.csv", "text/csv")
    
    if not w_df.empty:
        w_exp = w_df.copy()
        w_exp['Date'] = w_exp['Date'].apply(format_euro_date)
        w_csv = w_exp.to_csv(index=False).encode('utf-8')
        c_b.download_button("📥 Weight History (CSV)", w_csv, "weight.csv", "text/csv")
