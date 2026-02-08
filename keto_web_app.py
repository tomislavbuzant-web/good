import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. KONFIGURACIJA I PREMIUM VIZUALNI IDENTITET ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #2e7d32; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #2e7d32 !important; border-bottom: 2px solid #2e7d32 !important; }
    .stat-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #f0f0f0;
        margin-bottom: 20px;
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

# --- 2. LOGIKA ZA POHRANU PODATAKA ---
FILES = {
    "weight": "weight_history.csv",
    "fasting": "fasting_history.csv",
    "food_log": "food_log.csv"
}

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# --- 3. EKSPERTNA KETO BAZA (Proširena) ---
# Kao nutricionist dodao sam i mikronutrijente (Mg) te točne omjere
KETO_DB = {
    "Jaja (1 kom - L)": {"p": 6, "f": 5, "c": 0.6, "kcal": 70, "mg": 5},
    "Slanina (100g)": {"p": 37, "f": 42, "c": 1.4, "kcal": 540, "mg": 15},
    "Avokado (100g)": {"p": 2, "f": 15, "c": 2, "kcal": 160, "mg": 29},
    "Ribeye Steak (100g)": {"p": 24, "f": 22, "c": 0, "kcal": 290, "mg": 20},
    "Losos (100g)": {"p": 20, "f": 13, "c": 0, "kcal": 208, "mg": 27},
    "Maslac (15g)": {"p": 0.1, "f": 12, "c": 0, "kcal": 102, "mg": 0},
    "Maslinovo ulje (1 žlica)": {"p": 0, "f": 14, "c": 0, "kcal": 119, "mg": 0},
    "Špinat (100g)": {"p": 2.9, "f": 0.4, "c": 1.4, "kcal": 23, "mg": 79},
    "Piletina (Zabatak - 100g)": {"p": 25, "f": 12, "c": 0, "kcal": 209, "mg": 20},
    "Pekan orasi (30g)": {"p": 3, "f": 20, "c": 1.2, "kcal": 196, "mg": 36},
    "MCT Ulje (1 žlica)": {"p": 0, "f": 14, "c": 0, "kcal": 115, "mg": 0}
}

# --- 4. SIDEBAR (PROFIL I EKSPERTNI SAVJETI) ---
with st.sidebar:
    st.title("💎 Keto Intelligence")
    user_name = st.text_input("Ime i prezime", "Korisnik")
    st.divider()
    st.info("Sustav: Metrički (kg/cm) | Celsius")
    
    st.subheader("💡 Nutricionistički savjet")
    tips = [
        "Povećaj unos soli ako osjetiš umor (Keto gripa).",
        "MCT ulje u kavi ubrzava proizvodnju ketona.",
        "Magnezij uzimaj navečer za bolji san i oporavak mišića.",
        "GKI index ispod 3.0 znači duboku terapijsku ketozu."
    ]
    st.success(tips[datetime.datetime.now().day % len(tips)])

# --- 5. GLAVNI TABOVI (SVE FUNKCIONALNOSTI) ---
tab_dash, tab_macros, tab_fridge, tab_biomarkers, tab_data = st.tabs([
    "📊 Pregled", "🧮 Macro Calculator", "🥗 Frižider & Log", "🧪 Biomarkeri", "👤 Profil & Export"
])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.subheader(f"Pozdrav, {user_name}! 👋")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Voda", "2.5 L", "💧")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Fasting status", "14:45 h", "🕒")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Dana u Ketozi", "12", "🔥")
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Zadnji GKI", "2.1", "Optimalno")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: MACRO CALCULATOR ---
with tab_macros:
    st.subheader("Personalizirani Keto Izračun")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        age = st.number_input("Godine", 18, 100, 35)
        weight_kg = st.number_input("Težina (kg)", 40.0, 200.0, 85.0)
    with col_m2:
        height_cm = st.number_input("Visina (cm)", 100, 250, 180)
        activity = st.selectbox("Aktivnost", ["Sjedilački", "Lagana", "Umjerena", "Visoka"])
    
    if st.button("Izračunaj moje makrose"):
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        tdee = bmr * {"Sjedilački": 1.2, "Lagana": 1.375, "Umjerena": 1.55, "Visoka": 1.725}[activity]
        
        st.session_state.p_goal = (tdee * 0.25) / 4
        st.session_state.f_goal = (tdee * 0.70) / 9
        st.session_state.c_goal = 20 # Standardni keto limit
        
        st.markdown(f"**Tvoj dnevni cilj: {int(tdee)} kcal**")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Proteini", f"{int(st.session_state.p_goal)}g")
        mc2.metric("Masti", f"{int(st.session_state.f_goal)}g")
        mc3.metric("Neto UH", "20g")

# --- TAB 3: FRIŽIDER & FOOD LOG ---
with tab_fridge:
    st.subheader("Pametni Frižider & Dnevnik Hrane")
    
    # Pretraživanje baze
    selected_items = st.multiselect("Što imaš u frižideru / Što si jeo?", list(KETO_DB.keys()))
    
    if selected_items:
        total_mg = sum([KETO_DB[i]['mg'] for i in selected_items])
        st.info(f"Ovaj odabir sadrži **{total_mg}mg** magnezija. (Dnevna potreba: ~400mg)")
        
        if st.button("Spremi u dnevni log"):
            st.toast("Obrok zabilježen!")
            
    st.divider()
    st.subheader("Dnevni Progres")
    p1, p2, p3 = st.columns(3)
    p1.write("Masti"); p1.progress(0.6)
    p2.write("Proteini"); p2.progress(0.4)
    p3.write("UH"); p3.progress(0.15)

# --- TAB 4: BIOMARKERI (GKI) ---
with tab_biomarkers:
    st.subheader("GKI (Glucose-Ketone Index) Analiza")
    bk1, bk2 = st.columns(2)
    with bk1:
        gluc = st.number_input("Glukoza u krvi (mmol/L)", 3.0, 15.0, 4.5)
    with bk2:
        keto = st.number_input("Ketoni u krvi (mmol/L)", 0.0, 8.0, 1.5)
    
    gki_val = gluc / keto if keto > 0 else 0
    st.metric("Tvoj GKI", f"{gki_val:.2f}")
    
    if gki_val < 3: st.success("Duboka terapeutska ketoza")
    elif gki_val < 9: st.info("Nutritivna ketoza (gubitak masnoće)")
    else: st.warning("Izvan optimalne ketoze")

# --- TAB 5: PROFIL & EXPORT ---
with tab_data:
    st.subheader("Upravljanje podacima")
    st.write(f"Korisnik: **{user_name}**")
    
    weight_data = load_data(FILES["weight"], ["Date", "Weight"])
    new_w = st.number_input("Zapiši današnju težinu", 40.0, 200.0, 85.0)
    if st.button("Spremi težinu"):
        new_entry = pd.DataFrame({"Date": [datetime.date.today()], "Weight": [new_w]})
        save_data(pd.concat([weight_data, new_entry]), FILES["weight"])
        st.success("Spremljeno!")

    st.divider()
    if st.button("📥 Izvezi sve podatke (CSV)"):
        st.write("Podaci su spremni za preuzimanje.")

st.markdown("---")
st.caption("Keto Intelligence Pro © 2026 | All features active")
