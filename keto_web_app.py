import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. KONFIGURACIJA I PREMIUM STILIZACIJA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .keto-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px; }
    div[data-testid="stMetricValue"] { color: #2e7d32; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e8f5e9; border-radius: 10px 10px 0 0; padding: 12px 20px; color: #1b5e20;
    }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Datoteke za pohranu
FILES = {
    "fast": "fasting_history.csv",
    "weight": "weight_history.csv",
    "water": "water_history.csv",
    "ketones": "ketone_history.csv"
}

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- 2. PROŠIRENA EKSPERTNA BAZA NAMIRNICA ---
USDA_KETO = {
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290, "magnesium": 20},
    "Jaja (L veličina)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70, "magnesium": 5},
    "Maslac (15g)": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100, "magnesium": 0},
    "Losos (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200, "magnesium": 27},
    "Avokado (Srednji)": {"fat": 21, "prot": 3, "carb": 3, "cal": 240, "magnesium": 58},
    "Špinat (100g)": {"fat": 0.4, "prot": 2.9, "carb": 1.4, "cal": 23, "magnesium": 79},
    "MCT Ulje (1 žlica)": {"fat": 14, "prot": 0, "carb": 0, "cal": 115, "magnesium": 0},
    "Orasi (30g)": {"fat": 18, "prot": 4, "carb": 2, "cal": 185, "magnesium": 45},
    "Slanina (2 šnite)": {"fat": 7, "prot": 6, "carb": 0, "cal": 90, "magnesium": 3}
}

# --- 3. SIDEBAR (EKSPERTNI PROFIL) ---
st.sidebar.title("💎 Premium Keto AI")
profile_pic = st.sidebar.file_uploader("Upload Profile", type=['jpg', 'png'])
if profile_pic: st.sidebar.image(profile_pic, width=100)

user_name = st.sidebar.text_input("Ime i prezime", "Korisnik")
st.sidebar.markdown("---")
st.sidebar.write("💡 **Keto Savjet Dana:**")
tips = [
    "Povećaj unos soli (elektrolita) ako osjetiš glavobolju.",
    "MCT ulje u kavi može ubrzati ulazak u ketozu.",
    "Kvaliteta sna je jednako važna kao i makrosi za gubitak masnoće.",
    "Testiraj ketone ujutro prije jela za najtočniji rezultat."
]
st.sidebar.info(tips[datetime.datetime.now().day % len(tips)])

# --- 4. GLAVNI TABOVI ---
tab_dashboard, tab_fast, tab_fridge, tab_biomarkers, tab_export = st.tabs([
    "📊 Dashboard", "🕒 Fasting & Water", "🥗 Keto Kuhinja", "🧪 Biomarkeri", "👤 Profil"
])

# --- TAB: DASHBOARD (PREGLED) ---
with tab_dashboard:
    st.title(f"Dobrodošao natrag, {user_name}!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cilj Kalorija", f"{st.session_state.get('tdee_goal', 2000)} kcal")
    with col2:
        st.metric("Neto UH Cilj", "< 25g")
    with col3:
        w_df = load_data(FILES["weight"], ["Date", "Weight_kg"])
        last_w = w_df["Weight_kg"].iloc[-1] if not w_df.empty else 0
        st.metric("Zadnja težina", f"{last_w} kg")
    with col4:
        st.metric("Status", "🔥 Masnoća-spaljivanje")

# --- TAB: FASTING & WATER (HIDRATACIJA) ---
with tab_fast:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🕒 Fasting Tracker")
        if 'start_time' not in st.session_state: st.session_state.start_time = None
        
        if not st.session_state.start_time:
            if st.button("🚀 Pokreni Post (16/8)"):
                st.session_state.start_time = datetime.datetime.now()
                st.rerun()
        else:
            elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
            st.metric("Vrijeme bez hrane", f"{elapsed:.2f} h")
            if st.button("🍽️ Završi Post"):
                f_history = load_data(FILES["fast"], ["Date", "Hours"])
                new_f = pd.DataFrame({"Date": [datetime.date.today()], "Hours": [round(elapsed, 2)]})
                save_data(pd.concat([f_history, new_f]), FILES["fast"])
                st.session_state.start_time = None
                st.rerun()
    
    with c2:
        st.subheader("💧 Hidratacija & Elektroliti")
        water_df = load_data(FILES["water"], ["Date", "Liters"])
        liters = st.slider("Koliko si pio danas? (L)", 0.0, 5.0, 2.0, 0.25)
        if st.button("Spremi unos vode"):
            new_water = pd.DataFrame({"Date": [datetime.date.today()], "Liters": [liters]})
            save_data(pd.concat([water_df, new_water]), FILES["water"])
            st.success("Unos vode spremljen!")

# --- TAB: KETO KUHINJA ---
with tab_fridge:
    st.subheader("🥗 Pametni Keto Frižider")
    items = st.multiselect("Što imaš pri ruci?", list(USDA_KETO.keys()))
    
    if items:
        total_magnesium = sum([USDA_KETO[i]['magnesium'] for i in items])
        st.markdown(f"""
        <div class="keto-card">
            <h4>Analiza obroka:</h4>
            <p>Magnezij u odabranom: <b>{total_magnesium}mg</b> (Dnevno trebaš ~400mg)</p>
        </div>
        """, unsafe_allow_html=True)
        
        search_query = "+".join(items).replace(" ", "+")
        st.markdown(f"🔍 [Pronađi premium recepte na DietDoctor](https://www.dietdoctor.com/low-carb/keto/recipes/search?s={search_query})")

# --- TAB: BIOMARKERI (KETONI & GKI) ---
with tab_biomarkers:
    st.subheader("🧪 Ketoni & Metabolizam")
    bk1, bk2 = st.columns(2)
    with bk1:
        ket_val = st.number_input("Ketoni u krvi (mmol/L)", 0.0, 8.0, 0.5, 0.1)
        gluc_val = st.number_input("Glukoza (mmol/L)", 2.0, 15.0, 4.5, 0.1)
    with bk2:
        gki = gluc_val / ket_val if ket_val > 0 else 0
        st.metric("GKI Index", round(gki, 2))
        if gki < 3: st.success("Duboka Ketoza (Terapeutska)")
        elif gki < 9: st.info("Optimalna Ketoza za mršavljenje")
        else: st.warning("Niska razina ketoze")

# --- TAB: PROFIL & CALCULATOR ---
with tab_export:
    st.subheader("👤 Tvoj Profil")
    age = st.number_input("Godine", 18, 100, 35)
    weight = st.number_input("Težina (kg)", 40, 250, 90)
    height = st.number_input("Visina (cm)", 100, 250, 180)
    
    if st.button("Ažuriraj ciljeve"):
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        st.session_state.tdee_goal = int(bmr * 1.2)
        st.success(f"Tvoj novi bazalni cilj je {st.session_state.tdee_goal} kcal!")

    st.divider()
    if st.button("📥 Izvezi sve podatke za liječnika"):
        st.write("Svi podaci su sinkronizirani u CSV datoteke lokalno.")
