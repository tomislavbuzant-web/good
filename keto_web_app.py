import streamlit as st
import datetime
import pandas as pd
import os
import random

# --- 1. KONFIGURACIJA I PODACI ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"
PROFILE_FILE = "user_profile.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- 2. PROŠIRENA BAZA OBROKA S NAMIRNICAMA I GRAMAŽOM ---
KETO_MEALS = [
    {
        "name": "Jaja sa slaninom i avokadom", 
        "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25,
        "ingredients": ["3 jaja (150g)", "Dimljena slanina (50g)", "Zreli avokado (100g)", "Maslac (10g)"]
    },
    {
        "name": "Keto Omelet sa špinatom i sirom", 
        "type": "Breakfast", "kcal": 400, "fat": 32, "carb": 4, "prot": 22,
        "ingredients": ["3 jaja (150g)", "Baby špinat (50g)", "Cheddar ili Gouda (30g)", "Maslinovo ulje (10ml)"]
    },
    {
        "name": "Losos s pečenim šparogama", 
        "type": "Lunch", "kcal": 600, "fat": 40, "carb": 5, "prot": 45,
        "ingredients": ["Filet lososa (200g)", "Zelene šparoge (150g)", "Maslinovo ulje (20ml)", "Limunov sok (15ml)"]
    },
    {
        "name": "Piletina u umaku od vrhnja i gljiva", 
        "type": "Lunch", "kcal": 650, "fat": 48, "carb": 7, "prot": 42,
        "ingredients": ["Pileći zabatak bez kosti (200g)", "Šampinjoni (100g)", "Mliječno vrhnje 30% m.m. (50ml)", "Svinjska mast ili puter (15g)"]
    },
    {
        "name": "Ribeye Steak s maslacem od češnjaka", 
        "type": "Dinner", "kcal": 800, "fat": 60, "carb": 0, "prot": 55,
        "ingredients": ["Ribeye odrezak (250g)", "Domaći maslac (30g)", "Češnjak (5g)", "Miješana zelena salata (100g)"]
    },
    {
        "name": "Tikvice 'Carbonara' s pancetom", 
        "type": "Dinner", "kcal": 550, "fat": 42, "carb": 9, "prot": 28,
        "ingredients": ["Tikvice (200g)", "Dimljena panceta (60g)", "Žumanjci (2 kom)", "Parmezan ribani (20g)"]
    },
    {
        "name": "Šaka oraha i badema", 
        "type": "Snack", "kcal": 200, "fat": 18, "carb": 4, "prot": 5,
        "ingredients": ["Sirovi bademi (15g)", "Orasi jezgra (15g)"]
    },
    {
        "name": "Grčki jogurt s borovnicama", 
        "type": "Snack", "kcal": 180, "fat": 12, "carb": 7, "prot": 10,
        "ingredients": ["Pravi grčki jogurt 10% m.m. (150g)", "Svježe borovnice (30g)"]
    },
]

# --- 3. LOGIKA IZRAČUNA MAKROSA ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    if spol == "Muško":
        bmr = 10 * tezina + 6.25 * visina - 5 * godine + 5
    else:
        bmr = 10 * tezina + 6.25 * visina - 5 * godine - 161
    
    act_multiplier = {"Sjedilački": 1.2, "Lagano": 1.375, "Umjereno": 1.55, "Vrlo aktivno": 1.725}
    tdee = bmr * act_multiplier[aktivnost]
    
    if cilj == "Gubitak masti": target_kcal = tdee * 0.8
    elif cilj == "Dobivanje mišića": target_kcal = tdee * 1.1
    else: target_kcal = tdee

    return {
        "kcal": int(target_kcal),
        "fat": int((target_kcal * 0.70) / 9),
        "prot": int((target_kcal * 0.25) / 4),
        "carb": int((target_kcal * 0.05) / 4)
    }

# --- 4. GLAVNI INTERFEJS ---
st.title("🥑 Keto Intelligence Pro")

tab_prof, tab_fast, tab_menu, tab_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Personalizirani Menu", "📈 Napredak"])

# --- TAB: PROFIL ---
with tab_prof:
    st.header("Korisnički Profil & Postavke")
    prof_df = load_data(PROFILE_FILE, ["Ime", "Prezime", "Spol", "Tezina", "Visina", "Godine", "Aktivnost", "Cilj"])
    init_data = prof_df.iloc[0] if not prof_df.empty else None

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            ime = st.text_input("Ime", value=init_data["Ime"] if init_data is not None else "")
            prezime = st.text_input("Prezime", value=init_data["Prezime"] if init_data is not None else "")
            spol = st.selectbox("Spol", ["Muško", "Žensko"], index=0 if init_data is None or init_data["Spol"]=="Muško" else 1)
        with c2:
            tezina = st.number_input("Težina (kg)", value=float(init_data["Tezina"]) if init_data is not None else 80.0)
            visina = st.number_input("Visina (cm)", value=float(init_data["Visina"]) if init_data is not None else 180.0)
            godine = st.number_input("Godine", value=int(init_data["Godine"]) if init_data is not None else 30)

        aktivnost = st.select_slider("Razina aktivnosti", options=["Sjedilački", "Lagano", "Umjereno", "Vrlo aktivno"], 
                                     value=init_data["Aktivnost"] if init_data is not None else "Umjereno")
        cilj = st.selectbox("Cilj", ["Gubitak masti", "Održavanje", "Dobivanje mišića"], 
                            index=0 if init_data is None or init_data["Cilj"]=="Gubitak masti" else 1)
        
        if st.form_submit_button("Spremi Profil"):
            new_profile = pd.DataFrame([{
                "Ime": ime, "Prezime": prezime, "Spol": spol, "Tezina": tezina, 
                "Visina": visina, "Godine": godine, "Aktivnost": aktivnost, "Cilj": cilj
            }])
            save_data(new_profile, PROFILE_FILE)
            st.success("Profil uspješno spremljen!")
            st.rerun()

# --- TAB: POST (TIMER) ---
with tab_fast:
    st.header("16/8 Timer")
    if 'start_time' not in st.session_state: st.session_state.start_time = None
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🚀 Kreni s postom", use_container_width=True):
            st.session_state.start_time = datetime.datetime.now()
    with col_b:
        if st.button("🍽️ Završi i spremi", use_container_width=True):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_f = pd.DataFrame({"Date": [datetime.date.today()], "Hours": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_f]), FAST_FILE)
                st.session_state.start_time = None
                st.rerun()
    
    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Vrijeme posta", f"{elapsed:.2f} h")

# --- TAB: PERSONALIZIRANI MENU ---
with tab_menu:
    prof_df = load_data(PROFILE_FILE, [])
    if prof_df.empty:
        st.warning("Molimo prvo ispunite profil u Tabu 'Profil'.")
    else:
        user = prof_df.iloc[0]
        m = calculate_macros(user["Spol"], user["Tezina"], user["Visina"], user["Godine"], user["Aktivnost"], user["Cilj"])
        
        st.info(f"Dobrodošao natrag {user['Ime']}! Tvoj cilj: {m['kcal']} kcal | 🧈 {m['fat']}g Masti | 🥩 {m['prot']}g Prot | 🥦 {m['carb']}g UH")
        
        if st.button("🪄 GENERIRAJ DNEVNI KETO MENU", use_container_width=True):
            b = random.choice([x for x in KETO_MEALS if x['type'] == "Breakfast"])
            l = random.choice([x for x in KETO_MEALS if x['type'] == "Lunch"])
            d = random.choice([x for x in KETO_MEALS if x['type'] == "Dinner"])
            s = random.choice([x for x in KETO_MEALS if x['type'] == "Snack"])
            
            tk, tf, tp, tc = b['kcal']+l['kcal']+d['kcal']+s['kcal'], b['fat']+l['fat']+d['fat']+s['fat'], b['prot']+l['prot']+d['prot']+s['prot'], b['carb']+l['carb']+d['carb']+s['carb']
            
            st.subheader("📋 Preporučeni meni")
            
            # Prikaz obroka vertikalno s detaljima namirnica
            for label, meal in [("Doručak", b), ("Ručak", l), ("Večera", d), ("Snack (opcionalno)", s)]:
                with st.expander(f"**{label}: {meal['name']}**", expanded=True):
                    st.write("**Potrebne namirnice:**")
                    for ing in meal['ingredients']:
                        st.write(f"- {ing}")
                    st.caption(f"Nutrijenti obroka: {meal['kcal']} kcal | M: {meal['fat']}g | P: {meal['prot']}g | UH: {meal['carb']}g")
            
            st.divider()
            st.subheader("📊 Dnevni Ukupno / Cilj")
            
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Kcal (ukupno / cilj)", f"{tk} / {m['kcal']}", delta=f"{tk-m['kcal']}", delta_color="inverse")
            res2.metric("Masti (ukupno / cilj)", f"{tf}g / {m['fat']}g", delta=f"{tf-m['fat']}g")
            res3.metric("Proteini (ukupno / cilj)", f"{tp}g / {m['prot']}g", delta=f"{tp-m['prot']}g")
            res4.metric("Net UH (ukupno / cilj)", f"{tc}g / {m['carb']}g", delta=f"{tc-m['carb']}g", delta_color="inverse")

# --- TAB: NAPREDAK ---
with tab_prog:
    st.header("📈 Pratitelj težine")
    c_w1, c_w2 = st.columns([1, 2])
    
    with c_w1:
        w_val = st.number_input("Unesi današnju težinu (kg):", min_value=30.0, max_value=250.0, step=0.1, key="weight_input")
        if st.button("Spremi težinu"):
            new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [w_val]})
            old_w = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
            save_data(pd.concat([old_w, new_w]), WEIGHT_FILE)
            st.success("Težina zabilježena!")
            st.rerun()
    
    with c_w2:
        w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
        if not w_df.empty:
            w_df['Date'] = pd.to_datetime(w_df['Date'])
            st.line_chart(w_df.set_index("Date"))
            st.table(w_df.tail(5))
