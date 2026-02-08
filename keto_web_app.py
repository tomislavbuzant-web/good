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
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNKCIJE I DATOTEKE ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

FILES = {"weight": "weight_history.csv", "profile": "user_profile.csv"}

# --- 3. PROŠIRENA BAZA IDEJA S MAKROSIMA ---
# Vrijednosti su aproksimacije za standardne keto porcije
MEAL_DETAILS = {
    "Doručak": [
        {"naziv": "3 Jaja sa slaninom i avokadom", "p": 25.5, "f": 45.0, "c": 3.5, "kcal": 520},
        {"naziv": "Keto kava (MCT + Maslac)", "p": 1.0, "f": 25.0, "c": 0.0, "kcal": 230},
        {"naziv": "Omelet sa špinatom i feta sirom", "p": 20.0, "f": 32.5, "c": 4.0, "kcal": 385}
    ],
    "Ručak": [
        {"naziv": "Losos na žaru i pečena brokula", "p": 35.0, "f": 28.5, "c": 5.0, "kcal": 410},
        {"naziv": "Piletina s maslacem i cvjetačom", "p": 40.5, "f": 35.0, "c": 6.5, "kcal": 510},
        {"naziv": "Tuna salata s jajima i maslinama", "p": 32.0, "f": 38.0, "c": 3.0, "kcal": 485}
    ],
    "Večera": [
        {"naziv": "Ribeye steak (250g) i šparoge", "p": 55.0, "f": 52.0, "c": 2.5, "kcal": 710},
        {"naziv": "Pečeni svinjski vrat", "p": 42.0, "f": 48.5, "c": 0.0, "kcal": 605},
        {"naziv": "Keto tacosi u listu salate", "p": 30.0, "f": 35.5, "c": 5.5, "kcal": 460}
    ]
}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("💎 Keto Intelligence")
    st.info("Jedinice: Metrički | Celsius")
    if os.path.exists(FILES["profile"]):
        prof = pd.read_csv(FILES["profile"])
        st.success(f"Učitan profil: {prof['Weight'].values[0]} kg")

# --- 5. TABOVI ---
tab_dash, tab_macros, tab_meals, tab_biomarkers, tab_data = st.tabs([
    "📊 Dashboard", "🧮 Kalkulator", "🥗 Hrana & Meal Plan", "🧪 Biomarkeri", "👤 Profil"
])

# --- TAB 2: KALKULATOR MAKROA (Poboljšan) ---
with tab_macros:
    st.subheader("Personalizirani Keto Izračun")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        age = st.number_input("Godine", 18, 100, 52, step=1)
        # Postavljeno na 0.5 interval kako si tražio
        weight_curr = st.number_input("Težina (kg)", 40.0, 200.0, 95.0, step=0.5, key="calc_w")
    with col_m2:
        height_cm = st.number_input("Visina (cm)", 100, 250, 173, step=1)
        activity = st.selectbox("Razina aktivnosti", ["Sjedilački", "Lagana", "Umjerena", "Visoka"])
    
    c_btn1, c_btn2 = st.columns(2)
    
    # Izračun TDEE i makrosa
    bmr = (10 * weight_curr) + (6.25 * height_cm) - (5 * age) + 5
    tdee = bmr * {"Sjedilački": 1.2, "Lagana": 1.375, "Umjerena": 1.55, "Visoka": 1.725}[activity]
    
    # Keto ratio: 70% Mast, 25% Protein, 5% UH (ili fiksno 20g)
    f_g = (tdee * 0.70) / 9
    p_g = (tdee * 0.25) / 4
    c_g = 20.0
    
    if c_btn1.button("🚀 Izračunaj makrose"):
        st.session_state.p_goal = round(p_g, 1)
        st.session_state.f_goal = round(f_g, 1)
        st.session_state.c_goal = 20.0
        st.session_state.kcal_goal = int(tdee)
        
    if c_btn2.button("🔄 Izračunaj opet"):
        st.rerun()

    if 'kcal_goal' in st.session_state:
        st.markdown(f"### Tvoji dnevni ciljevi: **{st.session_state.kcal_goal} kcal**")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Proteini", f"{st.session_state.p_goal} g")
        mc2.metric("Masti", f"{st.session_state.f_goal} g")
        mc3.metric("Neto UH", f"{st.session_state.c_goal} g")
        
        if st.button("💾 Spremi ove podatke u profil"):
            prof_df = pd.DataFrame({
                "Age": [age], "Weight": [weight_curr], "Height": [height_cm],
                "Kcal": [st.session_state.kcal_goal], "P": [st.session_state.p_goal], "F": [st.session_state.f_goal]
            })
            save_data(prof_df, FILES["profile"])
            st.success("Profil uspješno ažuriran!")

# --- TAB 3: MEAL PLANER (S makronutrijentima) ---
with tab_meals:
    st.subheader("📋 Dnevni Meal Planer s Makrosima")
    
    if st.button("🔄 Generiraj novi plan obroka"):
        st.session_state.daily_plan = {
            "Doručak": random.choice(MEAL_DETAILS["Doručak"]),
            "Ručak": random.choice(MEAL_DETAILS["Ručak"]),
            "Večera": random.choice(MEAL_DETAILS["Večera"])
        }
    
    if 'daily_plan' in st.session_state:
        total_p, total_f, total_c, total_k = 0, 0, 0, 0
        for obrok, podaci in st.session_state.daily_plan.items():
            st.markdown(f"""
            <div class="meal-box">
                <strong>{obrok}: {podaci['naziv']}</strong><br>
                <small>🔥 {podaci['kcal']} kcal | 🥩 P: {podaci['p']}g | 🥑 M: {podaci['f']}g | 🥦 UH: {podaci['c']}g</small>
            </div>
            """, unsafe_allow_html=True)
            total_p += podaci['p']; total_f += podaci['f']
            total_c += podaci['c']; total_k += podaci['kcal']
            
        st.divider()
        st.markdown(f"**Ukupno za plan:** {total_k} kcal | P: {total_p:.1f}g | M: {total_f:.1f}g | UH: {total_c:.1f}g")

# --- OSTALI TABOVI (Dashboard, Biomarkeri, Profil) ---
with tab_dash:
    st.subheader("Brzi Pregled")
    if 'kcal_goal' in st.session_state:
        st.write(f"Cilj: {st.session_state.kcal_goal} kcal | Trenutna težina: {weight_curr} kg")
    st.info("Savjet: Pij 0.3 dcl vode po kilogramu težine.")

with tab_biomarkers:
    st.subheader("GKI Analiza")
    bk1, bk2 = st.columns(2)
    glu = bk1.number_input("Glukoza (mmol/L)", 3.0, 12.0, 4.5, step=0.1)
    ket = bk2.number_input("Ketoni (mmol/L)", 0.1, 8.0, 1.5, step=0.1)
    st.metric("GKI Index", f"{glu/ket:.2f}")

with tab_data:
    st.subheader("Povijest i Export")
    w_df = load_data(FILES["weight"], ["Date", "Weight"])
    new_w = st.number_input("Zapiši težinu (kg)", 40.0, 200.0, 95.0, step=0.5, key="final_w")
    if st.button("Spremi u dnevnik"):
        new_entry = pd.DataFrame({"Date": [datetime.date.today()], "Weight": [new_w]})
        save_data(pd.concat([w_df, new_entry], ignore_index=True), FILES["weight"])
        st.rerun()
    if not w_df.empty:
        st.line_chart(w_df.set_index("Date"))
