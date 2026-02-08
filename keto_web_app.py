import streamlit as st
import datetime
import pandas as pd
import os
import random
import plotly.express as px

# --- 1. KONFIGURACIJA I PODACI ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

PROFILE_FILE = "user_profile.csv"
FAST_FILE = "fasting_history.csv"

def save_data(df, filename): df.to_csv(filename, index=False)
def load_data(filename, columns):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- 2. BAZA OBROKA (Skraćeni prikaz za kod, u aplikaciji je 80+) ---
# (Ovdje ide onaj veliki popis KETO_MEALS iz prošlog odgovora)
KETO_MEALS = [
    # DORUČAK
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, "ingredients": ["3 jaja", "Slanina (50g)", "Avokado (100g)"], "preparation": "Ispecite slaninu i jaja na maslacu."},
    {"name": "Keto Omelet sa špinatom", "type": "Breakfast", "kcal": 420, "fat": 34, "carb": 4, "prot": 24, "ingredients": ["3 jaja", "Špinat (50g)", "Feta sir (30g)"], "preparation": "Umutite i ispecite na tavi."},
    # RUČAK
    {"name": "Piletina u curry umaku", "type": "Lunch", "kcal": 610, "fat": 45, "carb": 7, "prot": 42, "ingredients": ["Piletina", "Kokosovo mlijeko", "Curry"], "preparation": "Dinstajte u tavi."},
    {"name": "Bolognese s tikvicama", "type": "Lunch", "kcal": 580, "fat": 42, "carb": 9, "prot": 38, "ingredients": ["Mljeveno meso", "Tikvice", "Umak od rajčice"], "preparation": "Tikvice narežite na špagete."},
    # VEČERA
    {"name": "Ribeye Steak", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 0, "prot": 52, "ingredients": ["Steak", "Maslac"], "preparation": "Pecite na jakoj vatri."},
    {"name": "Tikvice Carbonara", "type": "Dinner", "kcal": 540, "fat": 42, "carb": 9, "prot": 26, "ingredients": ["Tikvice", "Panceta", "Jaja"], "preparation": "Umiješajte žumanjke na kraju."},
    # SNACK
    {"name": "Bademi i orasi", "type": "Snack", "kcal": 190, "fat": 17, "carb": 3, "prot": 6, "ingredients": ["Orašasti plodovi"], "preparation": "Spremno."},
    {"name": "Masline i sir", "type": "Snack", "kcal": 280, "fat": 26, "carb": 3, "prot": 10, "ingredients": ["Masline", "Sir"], "preparation": "Narežite."}
]
# ... (Dodaj ovdje sve ostale recepte iz prošle poruke da lista bude puna)

# --- 3. POMOĆNE FUNKCIJE ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    bmr = (10 * tezina + 6.25 * visina - 5 * godine + 5) if spol == "Muško" else (10 * tezina + 6.25 * visina - 5 * godine - 161)
    act_mult = {"Sjedilački": 1.2, "Lagano": 1.375, "Umjereno": 1.55, "Vrlo aktivno": 1.725}
    tdee = bmr * act_mult[aktivnost]
    target_kcal = tdee * 0.8 if cilj == "Gubitak masti" else (tdee * 1.1 if cilj == "Dobivanje mišića" else tdee)
    return {"kcal": int(target_kcal), "fat": int((target_kcal * 0.7) / 9), "prot": int((target_kcal * 0.25) / 4), "carb": int((target_kcal * 0.05) / 4)}

# --- 4. UI TABS ---
t_prof, t_fast, t_menu, t_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Menu", "📈 Napredak"])

# --- TAB: PROFIL ---
with t_prof:
    st.header("Korisnički Profil")
    p_df = load_data(PROFILE_FILE, ["Ime", "Spol", "Tezina", "Visina", "Godine", "Aktivnost", "Cilj"])
    init = p_df.iloc[0] if not p_df.empty else None
    with st.form("p_form"):
        c1, c2 = st.columns(2)
        with c1:
            ime = st.text_input("Ime", value=init["Ime"] if init is not None else "")
            spol = st.selectbox("Spol", ["Muško", "Žensko"], index=0 if init is None or init["Spol"]=="Muško" else 1)
            godine = st.number_input("Godine", value=int(init["Godine"]) if init is not None else 30)
        with c2:
            tezina = st.number_input("Težina (kg)", value=float(init["Tezina"]) if init is not None else 80.0)
            visina = st.number_input("Visina (cm)", value=float(init["Visina"]) if init is not None else 180.0)
            cilj = st.selectbox("Cilj", ["Gubitak masti", "Održavanje", "Dobivanje mišića"])
        aktivnost = st.select_slider("Aktivnost", options=["Sjedilački", "Lagano", "Umjereno", "Vrlo aktivno"])
        if st.form_submit_button("Spremi"):
            save_data(pd.DataFrame([{"Ime": ime, "Spol": spol, "Tezina": tezina, "Visina": visina, "Godine": godine, "Aktivnost": aktivnost, "Cilj": cilj}]), PROFILE_FILE)
            st.success("Profil spremljen!")

# --- TAB: POST (FASTING) ---
with t_fast:
    st.header("Intermittent Fasting Tajmer")
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.datetime_input("Početak posta", datetime.datetime.now())
        duration = st.selectbox("Cilj (sati)", [16, 18, 20, 24], index=0)
    
    if st.button("Završi i spremi post"):
        now = datetime.datetime.now()
        diff = now - start_time
        hours_fasted = round(diff.total_seconds() / 3600, 2)
        f_df = load_data(FAST_FILE, ["Datum", "Sati"])
        new_f = pd.DataFrame([{"Datum": now.strftime("%Y-%m-%d"), "Sati": hours_fasted}])
        save_data(pd.concat([f_df, new_f]), FAST_FILE)
        st.balloons()
        st.success(f"Spremljeno: Postili ste {hours_fasted} sati!")

# --- TAB: MENU ---
with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: 
        st.warning("Prvo ispunite profil.")
    else:
        u = p_df.iloc[0]
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        
        # Generator menu-a (ista logika kao prije)
        if st.button("🪄 GENERIRAJ NOVI MENU"):
            b_list = [x for x in KETO_MEALS if x['type'] == "Breakfast"]
            l_list = [x for x in KETO_MEALS if x['type'] == "Lunch"]
            d_list = [x for x in KETO_MEALS if x['type'] == "Dinner"]
            s_list = [x for x in KETO_MEALS if x['type'] == "Snack"]
            
            # Traženje najbolje kombinacije
            best = min([{"m": [random.choice(b_list), random.choice(l_list), random.choice(d_list), random.choice(s_list)]} for _ in range(500)], 
                       key=lambda x: abs(sum(item['kcal'] for item in x['m']) - m['kcal']))
            
            for meal in best['m']:
                with st.expander(f"{meal['type']}: {meal['name']} ({meal['kcal']} kcal)"):
                    st.write(f"**Sastojci:** {', '.join(meal['ingredients'])}")
                    st.info(f"**Upute:** {meal['preparation']}")

# --- TAB: NAPREDAK ---
with t_prog:
    st.header("Analitika Napretka")
    f_df = load_data(FAST_FILE, ["Datum", "Sati"])
    if not f_df.empty:
        fig = px.line(f_df, x="Datum", y="Sati", title="Povijest Posta", markers=True)
        st.plotly_chart(fig)
    else:
        st.info("Još nema podataka o postu.")
