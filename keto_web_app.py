import streamlit as st
import datetime
import pandas as pd
import os
import random

# --- 1. CONFIG & DATA ---
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

# --- 3. LOGIKA IZRAČUNA ---
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

# --- 4. APP INTERFACE ---
tab_prof, tab_fast, tab_menu, tab_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Personalizirani Menu", "📈 Napredak"])

# --- TAB: PROFIL ---
with tab_prof:
    st.header("Korisnički Profil")
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

        aktivnost = st.select_slider("Aktivnost", options=["Sjedilački", "Lagano", "Umjereno", "Vrlo aktivno"], 
                                     value=init_data["Aktivnost"] if init_data is not None else "Umjereno")
        cilj = st.selectbox("Cilj", ["Gubitak masti", "Održavanje", "Dobivanje mišića"], 
                            index=0 if init_data is None or init_data["Cilj"]=="Gubitak masti" else 1)
        
        if st.form_submit_button("Spremi Profil"):
            save_data(pd.DataFrame([{"Ime": ime, "Prezime": prezime, "Spol": spol, "Tezina": tezina, "Visina": visina, "Godine": godine, "Aktivnost": aktivnost, "Cilj": cilj}]), PROFILE_FILE)
            st.success("Profil spremljen!")
            st.rerun()

# --- TAB: POST ---
with tab_fast:
    st.header("16/8 Timer")
    if 'start_time' not in st.session_state: st.session_state.start_time = None
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Kreni s postom"):
            st.session_state.start_time = datetime.datetime.now()
    with c2:
        if st.button("🍽️ Završi i spremi"):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_f = pd.DataFrame({"Date": [datetime.date.today()], "Hours": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_f]), FAST_FILE)
                st.session_state.start_time = None
                st.rerun()
    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Vrijeme posta", f"{elapsed:.2f} h")

# --- TAB: MENU ---
with tab_menu:
    prof_df = load_data(PROFILE_FILE, [])
    if prof_df.empty:
        st.warning("Prvo ispunite profil.")
    else:
        user = prof_df.iloc[0]
        m = calculate_macros(user["Spol"], user["Tezina"], user["Visina"], user["Godine"], user["Aktivnost"], user["Cilj"])
        
        st.info(f"Dobrodošao natrag {user['Ime']}! Tvoj cilj: {m['kcal']} kcal | 🧈 {m['fat']}g Masti | 🥩 {m['prot']}g Prot | 🥦 {m['carb']}g UH")
        
        if st.button("🪄 GENERIRAJ DNEVNI KETO MENU"):
            b = random.choice([x for x in KETO_MEALS if x['type'] == "Breakfast"])
            l = random.choice([x for x in KETO_MEALS if x['type'] == "Lunch"])
            d = random.choice([x for x in KETO_MEALS if x['type'] == "Dinner"])
            s = random.choice([x for x in KETO_MEALS if x['type'] == "Snack"])
            
            tk, tf, tp, tc = b['kcal']+l['kcal']+d['kcal']+s['kcal'], b['fat']+l['fat']+d['fat']+s['fat'], b['prot']+l['prot']+d['prot']+s['prot'], b['carb']+l['carb']+d['carb']+s['carb']
            
            col1, col2, col3, col4 = st.columns(4)
            col1.success(f"🌅 {b['name']}")
            col2.success(f"☀️ {l['name']}")
            col3.success(f"🌙 {d['name']}")
            col4.success(f"🍿 {s['name']}")
            
            st.subheader("Dnevni Ukupno vs Cilj")
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Kcal", f"{tk}", f"{tk-m['kcal']} od cilja", delta_color="inverse")
            res2.metric("Masti", f"{tf}g", f"{tf-m['fat']}g")
            res3.metric("Proteini", f"{tp}g", f"{tp-m['prot']}g")
            res4.metric("Net UH", f"{tc}g", f"{tc-m['carb']}g", delta_color="inverse")

# --- TAB: NAPREDAK (VRAĆENO) ---
with tab_prog:
    st.header("📈 Pratitelj težine")
    w_val = st.number_input("Težina (kg):", min_value=30.0, step=0.1, key="prog_w")
    if st.button("Spremi težinu"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [w_val]})
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), new_w]), WEIGHT_FILE)
        st.success("Spremljeno!")
        st.rerun()
    
    w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_df.empty:
        w_df['Date'] = pd.to_datetime(w_df['Date'])
        st.line_chart(w_df.set_index("Date"))
        st.table(w_df.tail(5))
