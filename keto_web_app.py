import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. KONFIGURACIJA I STILIZACIJA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f1f3f5; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #2e7d32; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 8px 8px 0 0; 
        padding: 10px 15px;
        border: 1px solid #ddd;
    }
    .stButton>button { border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Datoteke za pohranu
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

# --- 2. KETO BAZA PODATAKA ---
USDA_KETO = {
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290},
    "Jaja (L veličina)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70},
    "Maslac (15g)": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100},
    "Losos (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200},
    "Avokado (Srednji)": {"fat": 21, "prot": 3, "carb": 3, "cal": 240},
    "Pileći zabatak (100g)": {"fat": 15, "prot": 20, "carb": 0, "cal": 210},
    "Kokosovo ulje (1 žlica)": {"fat": 14, "prot": 0, "carb": 0, "cal": 120},
    "Slanina (2 šnite)": {"fat": 7, "prot": 6, "carb": 0, "cal": 90},
    "Špinat (100g)": {"fat": 0.4, "prot": 2.9, "carb": 1.4, "cal": 23},
    "Pekan orasi (30g)": {"fat": 20, "prot": 3, "carb": 1.2, "cal": 200}
}

# --- 3. SIDEBAR (PROFIL) ---
st.sidebar.title("🥑 Keto Pro Profil")
profile_pic = st.sidebar.file_uploader("Učitaj fotografiju", type=['jpg', 'png'])

if profile_pic is not None:
    st.sidebar.image(profile_pic, width=120)

user_full_name = st.sidebar.text_input("Ime i prezime", "Korisnik")
st.sidebar.info("Sustav: Metrički (kg/cm) & Celzijus")

# --- 4. GLAVNI TABOVI ---
tab_fast, tab_macro, tab_fridge, tab_profile = st.tabs([
    "🕒 Fasting Tracker", "🧮 Macro Calculator", "🥗 Frižider & Recepti", "👤 Profil & Izvoz"
])

# --- TAB 1: FASTING (POST) ---
with tab_fast:
    st.header("16/8 Fasting Clock")
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Pokreni post sada"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ Završi post i zapiši"):
            if st.session_state.start_time:
                # Popravljen izračun trajanja
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_entry = pd.DataFrame({
                    "Date": [datetime.date.today().strftime('%Y-%m-%d')], 
                    "Hours": [round(duration, 2)]
                })
                history = load_data(FAST_FILE, ["Date", "Hours"])
                save_data(pd.concat([history, new_entry], ignore_index=True), FAST_FILE)
                st.session_state.start_time = None
                st.success(f"Zapisano: {duration:.2f} sati posta!")
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Protekao vrijeme", f"{elapsed:.2f} h")
        st.progress(min(elapsed/16, 1.0))

# --- TAB 2: MACRO CALCULATOR ---
with tab_macro:
    st.header("Personalizirani Keto Kalkulator")
    mc1, mc2 = st.columns(2)
    with mc1:
        age = st.number_input("Godine", 18, 100, 35)
        weight_kg = st.number_input("Trenutna težina (kg)", 40.0, 250.0, 90.0)
    with mc2:
        height_cm = st.number_input("Visina (cm)", 100, 250, 180)
        activity_lvl = st.selectbox("Razina aktivnosti", ["Sjedilački", "Lagana", "Umjerena", "Visoka"])

    if st.button("Izračunaj dnevne ciljeve"):
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        act_map = {"Sjedilački": 1.2, "Lagana": 1.375, "Umjerena": 1.55, "Visoka": 1.725}
        tdee = bmr * act_map[activity_lvl]
        
        st.session_state.f_goal = (tdee * 0.70) / 9
        st.session_state.p_goal = (tdee * 0.25) / 4
        st.session_state.c_goal = (tdee * 0.05) / 4
        
        st.success(f"Dnevni cilj: {int(tdee)} kalorija")
        m1, m2, m3 = st.columns(3)
        m1.metric("Masti (g)", f"{int(st.session_state.f_goal)}g")
        m2.metric("Proteini (g)", f"{int(st.session_state.p_goal)}g")
        m3.metric("Neto UH (g)", f"{int(st.session_state.c_goal)}g")

# --- TAB 3: FRIŽIDER & RECEPTI ---
with tab_fridge:
    st.header("Pametni Frižider")
    st.subheader("Što imate u kuhinji?")
    items_in_fridge = st.multiselect("Odaberite namirnice:", list(USDA_KETO.keys()))
    
    if items_in_fridge:
        st.divider()
        if 'p_goal' in st.session_state:
            prim_food = items_in_fridge[0]
            p_per_100 = USDA_KETO[prim_food]['prot']
            if p_per_100 > 0:
                needed_grams = int((st.session_state.p_goal / p_per_100) * 100)
                st.info(f"Da pogodite protein cilj koristeći **{prim_food}**, trebate pojesti **{needed_grams}g**.")
                
                f_in_food = (needed_grams / 100) * USDA_KETO[prim_food]['fat']
                extra_fat = max(0, int((st.session_state.f_goal - f_in_food) / 12))
                st.write(f"➡️ Dodajte **{extra_fat} žlica** masnoće (maslac/ulje) za savršen keto omjer.")
        else:
            st.warning("Prvo izračunajte makrose u Tabu 2!")

        search = "+".join(items_in_fridge).replace(" ", "+")
        st.subheader("🔍 Preporučeni Recepti")
        st.markdown(f"📖 [DietDoctor Recepti](https://www.dietdoctor.com/low-carb/keto/recipes/search?s={search})")
        st.markdown(f"🎥 [Headbanger's Kitchen (Video)](https://www.youtube.com/@HeadbangersKitchen/search?query={search})")

# --- TAB 4: PROFIL & IZVOZ ---
with tab_profile:
    st.header(f"Podaci: {user_full_name}")
    
    weight_hist = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    new_w = st.number_input("Unesi novu težinu (kg)", 30.0, 250.0, 90.0)
    if st.button("Spremi težinu"):
        w_entry = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [new_w]})
        save_data(pd.concat([weight_hist, w_entry], ignore_index=True), WEIGHT_FILE)
        st.rerun()

    if not weight_hist.empty:
        st.subheader("Trend težine")
        w_plot = weight_hist.copy()
        w_plot['Date'] = pd.to_datetime(w_plot['Date'])
        st.line_chart(w_plot.set_index('Date'))

    st.divider()
    if st.button("Pripremi podatke za izvoz"):
        f_hist = load_data(FAST_FILE, ["Date", "Hours"])
        if not f_hist.empty:
            f_hist['Date'] = f_hist['Date'].apply(format_euro_date)
            st.download_button("📥 Preuzmi Fasting log (CSV)", f_hist.to_csv(index=False), "post_izvoz.csv")
