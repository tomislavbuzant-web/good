import streamlit as st
import datetime
import pandas as pd
import os
import random
from PIL import Image

# --- 1. KONFIGURACIJA I DIZAJN ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #2e7d32; font-weight: 800; }
    .meal-box {
        padding: 10px 0px;
        border-bottom: 1px solid #eee;
        margin-bottom: 10px;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIKA ZA VIŠE KORISNIKA ---
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Zadano"

def get_user_folder(user):
    path = f"data/{user}"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# --- 3. BAZA SUPLEMENATA (EKSPERTNI SUSTAV) ---
SUPPLEMENT_DB = {
    "Magnezij": "Pomaže u radu mišića i smiruje živčani sustav. Najbolje uzeti: Navečer, 30 min prije spavanja.",
    "Omega 3": "Smanjuje upalne procese i podržava zdravlje srca. Najbolje uzeti: Uz obrok koji sadrži masti.",
    "MCT Ulje": "Brzi izvor energije i potiče proizvodnju ketona. Najbolje uzeti: Ujutro na tašte ili u kavi.",
    "Kalij": "Regulira krvni tlak i ravnotežu tekućine. Najbolje uzeti: Uz obrok.",
    "Vitamin D3": "Podržava imunitet i zdravlje kostiju. Najbolje uzeti: Ujutro uz obrok s mastima.",
    "Elektroliti": "Sprječavaju 'keto gripu' i dehidraciju. Najbolje uzeti: Tijekom dana u vodi."
}

# --- 4. SIDEBAR - MULTI-USER SELECTOR ---
with st.sidebar:
    st.title("💎 Keto Intelligence")
    
    # Upravljanje korisnicima
    existing_users = [d for d in os.listdir("data")] if os.path.exists("data") else ["Zadano"]
    new_user = st.text_input("Dodaj novog korisnika:")
    if st.button("Kreiraj profil"):
        if new_user: 
            get_user_folder(new_user)
            st.rerun()
            
    st.session_state.current_user = st.selectbox("Odaberi korisnika:", existing_users)
    st.write(f"Trenutni profil: **{st.session_state.current_user}**")

user_path = get_user_folder(st.session_state.current_user)

# --- 5. TABOVI ---
tab_dash, tab_macros, tab_meals, tab_supps, tab_data = st.tabs([
    "📊 Dashboard", "🧮 Kalkulator", "🥗 Meal Plan", "💊 Suplementi", "👤 Profil & Export"
])

# --- TAB: KALKULATOR (Default 52, 95, 173) ---
with tab_macros:
    st.subheader("Keto Kalkulator")
    c1, c2 = st.columns(2)
    age = c1.number_input("Godine", 18, 100, 52)
    weight = c1.number_input("Težina (kg)", 40.0, 200.0, 95.0, step=0.5)
    height = c2.number_input("Visina (cm)", 100, 250, 173)
    sex = c2.selectbox("Spol", ["Male", "Female"])
    activity = st.selectbox("Aktivnost", ["Sjedilački", "Lagana", "Umjerena", "Visoka"])

    if st.button("🚀 Izračunaj i Spremi"):
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if sex == "Male" else -161)
        tdee = bmr * {"Sjedilački": 1.2, "Lagana": 1.375, "Umjerena": 1.55, "Visoka": 1.725}[activity]
        st.session_state.p_g = round((tdee * 0.25) / 4, 1)
        st.session_state.f_g = round((tdee * 0.70) / 9, 1)
        st.session_state.kcal = int(tdee)
        
        # Spremanje u profil korisnika
        prof_df = pd.DataFrame({
            "User": [st.session_state.current_user], "Age": [age], "Weight": [weight],
            "Sex": [sex], "Kcal": [st.session_state.kcal], "P": [st.session_state.p_g], "F": [st.session_state.f_g]
        })
        prof_df.to_csv(f"{user_path}/profile.csv", index=False)
        st.success("Podaci spremljeni!")

# --- TAB: MEAL PLAN (Bez bijele pozadine) ---
with tab_meals:
    st.subheader("Dnevni Meal Planer")
    # ... (kod za MEAL_DETAILS ostaje isti iz prošle poruke)
    if st.button("🔄 Generiraj plan"):
        # (Logika generiranja iz prošle poruke...)
        st.session_state.plan = "Generirano" # Placeholder za primjer

    st.markdown("""<div class="meal-box"><strong>Doručak:</strong> 3 Jaja sa slaninom i avokadom<br><small>520 kcal | P: 25.5g | M: 45.0g</small></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="meal-box"><strong>Ručak:</strong> Losos i brokula<br><small>410 kcal | P: 35.0g | M: 28.5g</small></div>""", unsafe_allow_html=True)

# --- TAB: SUPLEMENTI (Novo!) ---
with tab_supps:
    st.subheader("💊 Moji Suplementi")
    
    all_supps = list(SUPPLEMENT_DB.keys()) + ["Ostalo"]
    selected_supp = st.selectbox("Dodaj suplement:", all_supps)
    
    if st.button("Dodaj u moj dnevnik"):
        supp_file = f"{user_path}/supplements.csv"
        current_supps = pd.read_csv(supp_file) if os.path.exists(supp_file) else pd.DataFrame(columns=["Name"])
        new_s = pd.DataFrame({"Name": [selected_supp]})
        pd.concat([current_supps, new_s]).drop_duplicates().to_csv(supp_file, index=False)
        st.toast(f"Dodano: {selected_supp}")

    st.divider()
    st.subheader("📋 Plan uzimanja")
    if os.path.exists(f"{user_path}/supplements.csv"):
        my_supps = pd.read_csv(f"{user_path}/supplements.csv")
        for s in my_supps["Name"]:
            info = SUPPLEMENT_DB.get(s, "Konzumirati prema uputama na pakiranju.")
            st.info(f"**{s}**: {info}")

# --- TAB: PROFIL & EXPORT ---
with tab_data:
    st.subheader("Korisnički Profil")
    
    # Upload slike
    img_file = st.file_uploader("Prenesi profilnu sliku", type=['png', 'jpg', 'jpeg'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=150)
        img.save(f"{user_path}/avatar.png")
    elif os.path.exists(f"{user_path}/avatar.png"):
        st.image(f"{user_path}/avatar.png", width=150)

    # Detalji profila
    name_surname = st.text_input("Ime i Prezime", "Korisnik")
    
    st.divider()
    st.subheader("📥 Export u Excel")
    ex_prof = st.checkbox("Profil i Makrosi", True)
    ex_weight = st.checkbox("Povijest težine", True)
    ex_supps = st.checkbox("Lista suplemenata", True)
    
    if st.button("Exportuj odabrano"):
        # Logika za generiranje Excela s više sheetova
        st.write("Excel datoteka se generira...")
        # (Ovdje bi išao pd.ExcelWriter za kompleksniji export)

