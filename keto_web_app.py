import streamlit as st
import datetime
import pandas as pd
import os
import random

# --- 1. KONFIGURACIJA I DIZAJN ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #2e7d32; font-weight: 800; }
    .stat-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #f0f0f0;
        margin-bottom: 20px;
    }
    .meal-box {
        padding: 15px;
        background-color: #f1f8e9;
        border-left: 5px solid #2e7d32;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        height: 3em;
        width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNKCIJE ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

FILES = {"weight": "weight_history.csv", "food_log": "food_log.csv"}

# --- 3. PROŠIRENA BAZA I RECEPTI ---
KETO_DB = {
    "Jaja (L veličina)": {"p": 6, "f": 5, "c": 0.6, "kcal": 70, "mg": 5},
    "Slanina (100g)": {"p": 37, "f": 42, "c": 1.4, "kcal": 540, "mg": 15},
    "Avokado (100g)": {"p": 2, "f": 15, "c": 2, "kcal": 160, "mg": 29},
    "Ribeye Steak (100g)": {"p": 24, "f": 22, "c": 0, "kcal": 290, "mg": 20},
    "Losos (100g)": {"p": 20, "f": 13, "c": 0, "kcal": 208, "mg": 27},
    "Maslac (15g)": {"p": 0.1, "f": 12, "c": 0, "kcal": 102, "mg": 0},
    "Špinat (100g)": {"p": 2.9, "f": 0.4, "c": 1.4, "kcal": 23, "mg": 79},
    "Pekan orasi (30g)": {"p": 3, "f": 20, "c": 1.2, "kcal": 196, "mg": 36}
}

MEAL_IDEAS = {
    "Doručak": ["3 Jaja sa slaninom i avokadom", "Keto kava s maslacem i MCT uljem", "Omelet sa špinatom i feta sirom"],
    "Ručak": ["Losos na žaru s pečenom brokulom", "Piletina s maslacem i cvjetačom", "Velika salata s tunom, jajima i maslinovim uljem"],
    "Večera": ["Ribeye steak s bazičnim začinima", "Pečeni svinjski vrat i šparoge", "Keto tacosi u listovima salate"]
}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("💎 Keto Intelligence")
    user_name = st.text_input("Ime", "Korisnik")
    st.divider()
    st.info("Mjerilo: Metrički | Celsius")

# --- 5. GLAVNI TABOVI ---
tab_dash, tab_macros, tab_meals, tab_biomarkers, tab_data = st.tabs([
    "📊 Dashboard", "🧮 Kalkulator", "🥗 Hrana & Meal Plan", "🧪 Biomarkeri", "👤 Profil"
])

# --- DASHBOARD ---
with tab_dash:
    st.subheader(f"Status za: {user_name}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Voda", "2.5 L", "💧")
    c2.metric("Vrijeme posta", "14:45 h", "🕒")
    c3.metric("Ketoni", "1.5 mmol/L", "🔥")

# --- MACRO CALCULATOR ---
with tab_macros:
    st.subheader("Personalizirani Keto Izračun")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        age = st.number_input("Godine", 18, 100, 35)
        weight_curr = st.number_input("Težina (kg)", 40.0, 200.0, 85.0, key="calc_w")
    with col_m2:
        height_cm = st.number_input("Visina (cm)", 100, 250, 180)
        activity = st.selectbox("Aktivnost", ["Sjedilački", "Lagana", "Umjerena", "Visoka"])
    
    if st.button("Izračunaj makrose"):
        bmr = (10 * weight_curr) + (6.25 * height_cm) - (5 * age) + 5
        tdee = bmr * {"Sjedilački": 1.2, "Lagana": 1.375, "Umjerena": 1.55, "Visoka": 1.725}[activity]
        st.session_state.p_goal = int((tdee * 0.25) / 4)
        st.session_state.f_goal = int((tdee * 0.70) / 9)
        st.session_state.kcal_goal = int(tdee)
        st.success(f"Dnevni cilj: {st.session_state.kcal_goal} kcal")

# --- MEAL PLANNER & HRANA ---
with tab_meals:
    st.subheader("📋 Dnevni Meal Planer")
    
    if 'kcal_goal' not in st.session_state:
        st.warning("Prvo izračunaj makrose u tabu 'Kalkulator'!")
    else:
        st.markdown(f"**Cilj: {st.session_state.kcal_goal} kcal | P: {st.session_state.p_goal}g | F: {st.session_state.f_goal}g | C: 20g**")
        
        if st.button("🔄 Generiraj novi plan obroka"):
            st.session_state.daily_plan = {
                "Doručak": random.choice(MEAL_IDEAS["Doručak"]),
                "Ručak": random.choice(MEAL_IDEAS["Ručak"]),
                "Večera": random.choice(MEAL_IDEAS["Večera"])
            }
        
        if 'daily_plan' in st.session_state:
            for meal, desc in st.session_state.daily_plan.items():
                st.markdown(f"""<div class="meal-box"><strong>{meal}:</strong> {desc}</div>""", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("🔍 Pretraga baze namirnica")
    selected = st.multiselect("Odaberi što si jeo:", list(KETO_DB.keys()))
    if selected:
        total_mg = sum([KETO_DB[i]['mg'] for i in selected])
        total_kcal = sum([KETO_DB[i]['kcal'] for i in selected])
        st.info(f"Unos: {total_kcal} kcal | {total_mg}mg Magnezija")

# --- BIOMARKERI ---
with tab_biomarkers:
    st.subheader("GKI Analiza")
    bk1, bk2 = st.columns(2)
    glu = bk1.number_input("Glukoza (mmol/L)", 3.0, 12.0, 4.5)
    ket = bk2.number_input("Ketoni (mmol/L)", 0.1, 8.0, 1.5)
    st.metric("GKI Index", f"{glu/ket:.2f}")

# --- PROFIL ---
with tab_data:
    st.subheader("Povijest Težine")
    weight_df = load_data(FILES["weight"], ["Date", "Weight"])
    new_w = st.number_input("Nova težina (kg)", 40.0, 200.0, 85.0, key="save_w")
    if st.button("Spremi"):
        new_entry = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight": [new_w]})
        save_data(pd.concat([weight_df, new_entry], ignore_index=True), FILES["weight"])
        st.rerun()
    if not weight_df.empty:
        st.line_chart(weight_df.set_index("Date"))
