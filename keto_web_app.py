import streamlit as st
import datetime
import pandas as pd
import os
import requests
import random

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

# --- 2. PROŠIRENA BAZA RECEPATA S MAKROSIMA ---
# Dodao sam makrose po obroku (približne vrijednosti za keto porciju)
KETO_MEALS = [
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25},
    {"name": "Keto Omelet sa špinatom i sirom", "type": "Breakfast", "kcal": 400, "fat": 32, "carb": 4, "prot": 22},
    {"name": "Chia puding s kokosovim mlijekom", "type": "Breakfast", "kcal": 350, "fat": 28, "carb": 6, "prot": 8},
    {"name": "Losos s pečenim šparogama", "type": "Lunch", "kcal": 600, "fat": 40, "carb": 5, "prot": 45},
    {"name": "Piletina u umaku od vrhnja i gljiva", "type": "Lunch", "kcal": 650, "fat": 48, "carb": 7, "prot": 42},
    {"name": "Cezar salata (bez krutona) s piletinom", "type": "Lunch", "kcal": 500, "fat": 35, "carb": 6, "prot": 38},
    {"name": "Ribeye Steak s maslacem od češnjaka", "type": "Dinner", "kcal": 800, "fat": 60, "carb": 0, "prot": 55},
    {"name": "Svinjska rebra s coleslaw salatom", "type": "Dinner", "kcal": 750, "fat": 55, "carb": 8, "prot": 40},
    {"name": "Tikvice 'Carbonara' s pancetom", "type": "Dinner", "kcal": 550, "fat": 42, "carb": 9, "prot": 28},
    {"name": "Šaka oraha i badema", "type": "Snack", "kcal": 200, "fat": 18, "carb": 4, "prot": 5},
    {"name": "Mjerica Wheya s bademovim mlijekom", "type": "Snack", "kcal": 150, "fat": 5, "carb": 2, "prot": 25},
    {"name": "Grčki jogurt s par bobica borovnica", "type": "Snack", "kcal": 180, "fat": 12, "carb": 7, "prot": 10},
]

# --- 3. APP INTERFACE ---
st.title("🥑 Keto Intelligence Pro")

tab1, tab2, tab3, tab4 = st.tabs(["🕒 Post", "🥗 Personalizirani Menu", "💊 Suplementi", "📈 Napredak"])

# --- TAB 1: FASTING (Standardno) ---
with tab1:
    st.header("16/8 Timer")
    if 'start_time' not in st.session_state: st.session_state.start_time = None
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Kreni s postom"):
            st.session_state.start_time = datetime.datetime.now()
            st.rerun()
    with c2:
        if st.button("🍽️ Završi i spremi"):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_fast = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Hours": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_fast]), FAST_FILE)
                st.session_state.start_time = None
                st.rerun()

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Vrijeme posta", f"{elapsed:.2f} h")
        st.progress(min(elapsed/16, 1.0))

# --- TAB 2: PERSONALIZIRANI MENU (NOVO) ---
with tab2:
    st.header("🧬 Keto Makro Kalkulator")
    
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        spol = st.selectbox("Spol", ["Muško", "Žensko"])
        težina = st.number_input("Težina (kg)", value=85.0)
    with col_k2:
        visina = st.number_input("Visina (cm)", value=180.0)
        godine = st.number_input("Godine", value=30)
    with col_k3:
        aktivnost = st.select_slider("Aktivnost", options=["Sjedilački", "Lagano", "Umjereno", "Vrlo aktivno"])
        cilj = st.selectbox("Cilj", ["Gubitak masti", "Održavanje", "Dobivanje mišića"])
    
    # Izračun BMR (Mifflin-St Jeor)
    if spol == "Muško":
        bmr = 10 * težina + 6.25 * visina - 5 * godine + 5
    else:
        bmr = 10 * težina + 6.25 * visina - 5 * godine - 161
        
    act_multiplier = {"Sjedilački": 1.2, "Lagano": 1.375, "Umjereno": 1.55, "Vrlo aktivno": 1.725}
    tdee = bmr * act_multiplier[aktivnost]
    
    if cilj == "Gubitak masti":
        target_kcal = tdee * 0.8
    elif cilj == "Dobivanje mišića":
        target_kcal = tdee * 1.1
    else:
        target_kcal = tdee

    # Keto Makrosi (70% Fat, 25% Prot, 5% Carb)
    target_fat = (target_kcal * 0.70) / 9
    target_prot = (target_kcal * 0.25) / 4
    target_carb = (target_kcal * 0.05) / 4

    st.info(f"📍 Tvoj dnevni cilj: **{int(target_kcal)} kcal** | 🧈 {int(target_fat)}g Masti | 🥩 {int(target_prot)}g Proteina | 🥦 {int(target_carb)}g Net UH")

    st.divider()
    
    if st.button("🪄 GENERIRAJ DNEVNI KETO MENU"):
        # Jednostavan random selection po kategorijama
        b_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Breakfast"])
        l_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Lunch"])
        d_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Dinner"])
        s_choice = random.choice([m for m in KETO_MEALS if m['type'] == "Snack"])
        
        total_kcal = b_choice['kcal'] + l_choice['kcal'] + d_choice['kcal'] + s_choice['kcal']
        total_fat = b_choice['fat'] + l_choice['fat'] + d_choice['fat'] + s_choice['fat']
        total_prot = b_choice['prot'] + l_choice['prot'] + d_choice['prot'] + s_choice['prot']
        total_carb = b_choice['carb'] + l_choice['carb'] + d_choice['carb'] + s_choice['carb']
        
        st.subheader("📋 Prijedlog menija za danas")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.write("🌅 **Doručak**")
            st.success(f"{b_choice['name']}")
        with m2:
            st.write("☀️ **Ručak**")
            st.success(f"{l_choice['name']}")
        with m3:
            st.write("🌙 **Večera**")
            st.success(f"{d_choice['name']}")
        with m4:
            st.write("🍿 **Snack**")
            st.success(f"{s_choice['name']}")
            
        st.divider()
        st.subheader("📊 Ukupni makrosi ovog menija")
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Kcal", f"{total_kcal}", delta=f"{int(total_kcal - target_kcal)} od cilja", delta_color="inverse")
        c_m2.metric("Masti", f"{total_fat}g", delta=f"{int(total_fat - target_fat)}g")
        c_m3.metric("Proteini", f"{total_prot}g", delta=f"{int(total_prot - target_prot)}g")
        c_m4.metric("Net UH", f"{total_carb}g", delta=f"{int(total_carb - target_carb)}g", delta_color="inverse")

# --- TAB 3: SUPPLEMENTS ---
with tab3:
    st.header("Suplementacija")
    st.info("Na keto dijeti gubiš više elektrolita (natrij, kalij, magnezij).")
    # ... ostatak koda za suplemente ...

# --- TAB 4: PROGRESS ---
with tab4:
    st.header("Pratitelj težine")
    weight_input = st.number_input("Unesi težinu (kg)", value=težina)
    if st.button("Spremi napredak"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [weight_input]})
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), new_w]), WEIGHT_FILE)
        st.rerun()
