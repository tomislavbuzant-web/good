import streamlit as st
import datetime
import pandas as pd
import os
import random

# --- 1. CONFIG & DATA PERSISTENCE ---
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

# --- 2. BAZA OBROKA ---
KETO_MEALS = [
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25},
    {"name": "Keto Omelet sa špinatom i sirom", "type": "Breakfast", "kcal": 400, "fat": 32, "carb": 4, "prot": 22},
    {"name": "Losos s pečenim šparogama", "type": "Lunch", "kcal": 600, "fat": 40, "carb": 5, "prot": 45},
    {"name": "Piletina u umaku od vrhnja i gljiva", "type": "Lunch", "kcal": 650, "fat": 48, "carb": 7, "prot": 42},
    {"name": "Ribeye Steak s maslacem od češnjaka", "type": "Dinner", "kcal": 800, "fat": 60, "carb": 0, "prot": 55},
    {"name": "Tikvice 'Carbonara' s pancetom", "type": "Dinner", "kcal": 550, "fat": 42, "carb": 9, "prot": 28},
    {"name": "Šaka oraha i badema", "type": "Snack", "kcal": 200, "fat": 18, "carb": 4, "prot": 5},
    {"name": "Grčki jogurt s borovnicama", "type": "Snack", "kcal": 180, "fat": 12, "carb": 7, "prot": 10},
]

# --- 3. POMOĆNE FUNKCIJE ZA KALKULACIJU ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    # Mifflin-St Jeor formula
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

# --- 4. APP INTERFACE ---
st.title("🥑 Keto Intelligence Pro")

tab_prof, tab_fast, tab_menu, tab_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Personalizirani Menu", "📈 Napredak"])

# --- TAB: PROFIL ---
with tab_prof:
    st.header("Korisnički Profil & Macro Postavke")
    prof_df = load_data(PROFILE_FILE, ["Ime", "Prezime", "Spol", "Tezina", "Visina", "Godine", "Aktivnost", "Cilj"])
    
    # Inicijalne vrijednosti ako profil ne postoji
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

    if init_data is not None:
        macros = calculate_macros(spol, tezina, visina, godine, aktivnost, cilj)
        st.subheader("Vaši Izračunati Macro podaci")
        
        col_res = st.columns(4)
        col_res[0].metric("Dnevni Kcal", f"{macros['kcal']}")
        col_res[1].metric("Masti (70%)", f"{macros['fat']}g")
        col_res[2].metric("Proteini (25%)", f"{macros['prot']}g")
        col_res[3].metric("Net UH (5%)", f"{macros['carb']}g")

# --- TAB: PERSONALIZIRANI MENU ---
with tab_menu:
    st.header("Generiranje Menija")
    prof_df = load_data(PROFILE_FILE, [])
    
    if prof_df.empty:
        st.warning("Molimo prvo ispunite profil kako bi izračunali vaše potrebe.")
    else:
        user = prof_df.iloc[0]
        macros = calculate_macros(user["Spol"], user["Tezina"], user["Visina"], user["Godine"], user["Aktivnost"], user["Cilj"])
        
        st.info(f"Dobrodošao natrag {user['Ime']}! Tvoj cilj je {macros['kcal']} kcal.")
        
        if st.button("🪄 GENERIRAJ DNEVNI KETO MENU"):
            b_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Breakfast"])
            l_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Lunch"])
            d_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Dinner"])
            s_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Snack"])
            
            total_kcal = b_choice['kcal'] + l_choice['kcal'] + d_choice['kcal'] + s_choice['kcal']
            
            m1, m2, m3, m4 = st.columns(4)
            m1.success(f"🌅 Doručak: {b_choice['name']}")
            m2.success(f"☀️ Ručak: {l_choice['name']}")
            m3.success(f"🌙 Večera: {d_choice['name']}")
            m4.success(f"🍿 Snack: {s_choice['name']}")
            
            st.metric("Ukupna energija", f"{total_kcal} kcal", delta=f"{total_kcal - macros['kcal']} kcal od cilja", delta_color="inverse")

# --- OSTALI TABOVI (Zadržani) ---
with tab_fast:
    st.header("16/8 Timer")
    # ... timer kod ...

with tab_prog:
    st.header("Napredak")
    # ... grafikon težine ...
