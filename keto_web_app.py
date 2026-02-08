import streamlit as st
import datetime
import pandas as pd
import os
import random

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"
PROFILE_FILE = "user_profile.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- 2. PROŠIRENA BAZA OBROKA (S SALATAMA I VIŠE OPCIJA) ---
KETO_MEALS = [
    # DORUČAK
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, "ingredients": ["3 jaja (150g)", "Slanina (50g)", "Avokado (100g)", "Maslac (10g)"]},
    {"name": "Keto Omelet sa špinatom", "type": "Breakfast", "kcal": 420, "fat": 34, "carb": 4, "prot": 24, "ingredients": ["3 jaja (150g)", "Špinat (50g)", "Feta sir (30g)", "Maslinovo ulje (10ml)"]},
    {"name": "Chia puding s kokosom", "type": "Breakfast", "kcal": 350, "fat": 28, "carb": 6, "prot": 12, "ingredients": ["Chia sjemenke (30g)", "Kokosovo mlijeko punomasno (150ml)", "Bademi listići (10g)"]},
    {"name": "Keto palačinke od bademovog brašna", "type": "Breakfast", "kcal": 480, "fat": 38, "carb": 8, "prot": 18, "ingredients": ["Bademovo brašno (40g)", "Krem sir (30g)", "2 jaja", "Maslac za pečenje (10g)"]},

    # RUČAK (S DODANIM SALATAMA)
    {"name": "Losos s pečenim šparogama", "type": "Lunch", "kcal": 620, "fat": 42, "carb": 6, "prot": 45, "ingredients": ["Filet lososa (200g)", "Šparoge (150g)", "Maslinovo ulje (20ml)", "Miješana zelena salata (100g) s limunom"]},
    {"name": "Piletina u vrhnju i gljivama", "type": "Lunch", "kcal": 680, "fat": 50, "carb": 8, "prot": 44, "ingredients": ["Pileći zabatak (220g)", "Šampinjoni (100g)", "Vrhnje 30% m.m. (60ml)", "Rikula salata (50g) s maslinovim uljem"]},
    {"name": "Juneći burger bez peciva", "type": "Lunch", "kcal": 700, "fat": 55, "carb": 5, "prot": 40, "ingredients": ["Mljevena junetina (200g)", "Cheddar sir (25g)", "Avokado (50g)", "Velika zdjela miješane salate (150g)"]},
    {"name": "Cezar salata (Keto verzija)", "type": "Lunch", "kcal": 580, "fat": 48, "carb": 7, "prot": 35, "ingredients": ["Piletina grill (150g)", "Rimski zelena salata (200g)", "Parmezan (30g)", "Cezar dresing na bazi majoneze (40ml)"]},
    {"name": "Tuna steak s blitvom", "type": "Lunch", "kcal": 520, "fat": 32, "carb": 5, "prot": 48, "ingredients": ["Tuna filet (200g)", "Blitva (200g)", "Maslinovo ulje (25ml)", "Češnjak (5g)"]},

    # VEČERA (S DODANIM SALATAMA)
    {"name": "Ribeye Steak s maslacem", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 2, "prot": 52, "ingredients": ["Ribeye odrezak (250g)", "Maslac (25g)", "Zelena salata (100g) s jabučnim octom"]},
    {"name": "Tikvice Carbonara", "type": "Dinner", "kcal": 540, "fat": 42, "carb": 9, "prot": 26, "ingredients": ["Tikvice spiralizirane (250g)", "Panceta (60g)", "Žumanjci (2 kom)", "Puter (10g)", "Salata od radiča (50g)"]},
    {"name": "Pečeni oslić s povrćem", "type": "Dinner", "kcal": 450, "fat": 30, "carb": 7, "prot": 38, "ingredients": ["Oslić filet (200g)", "Brokula na pari (150g)", "Maslinovo ulje (20ml)", "Matovilac salata (50g)"]},
    {"name": "Svinjski kotlet s kupus salatom", "type": "Dinner", "kcal": 610, "fat": 45, "carb": 6, "prot": 42, "ingredients": ["Svinjski kotlet (200g)", "Svinjska mast (15g)", "Kupus salata svježa (200g) s uljem i octom"]},

    # SNACK
    {"name": "Orašasti plodovi", "type": "Snack", "kcal": 210, "fat": 19, "carb": 4, "prot": 6, "ingredients": ["Orasi i bademi (30g)"]},
    {"name": "Grčki jogurt", "type": "Snack", "kcal": 190, "fat": 15, "carb": 7, "prot": 9, "ingredients": ["Grčki jogurt 10% m.m. (150g)", "Par borovnica (15g)"]},
    {"name": "Kuhana jaja s majonezom", "type": "Snack", "kcal": 250, "fat": 20, "carb": 2, "prot": 14, "ingredients": ["2 kuhana jaja", "Domaća majoneza (15g)"]},
    {"name": "Masline i sir", "type": "Snack", "kcal": 280, "fat": 26, "carb": 3, "prot": 10, "ingredients": ["Masline (50g)", "Tvrdi sir/Ementaler (40g)"]}
]

# --- 3. LOGIKA I APP ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    bmr = (10 * tezina + 6.25 * visina - 5 * godine + 5) if spol == "Muško" else (10 * tezina + 6.25 * visina - 5 * godine - 161)
    act_mult = {"Sjedilački": 1.2, "Lagano": 1.375, "Umjereno": 1.55, "Vrlo aktivno": 1.725}
    tdee = bmr * act_mult[aktivnost]
    if cilj == "Gubitak masti": target_kcal = tdee * 0.8
    elif cilj == "Dobivanje mišića": target_kcal = tdee * 1.1
    else: target_kcal = tdee
    return {"kcal": int(target_kcal), "fat": int((target_kcal * 0.70) / 9), "prot": int((target_kcal * 0.25) / 4), "carb": int((target_kcal * 0.05) / 4)}

st.title("🥑 Keto Intelligence Pro")
t_prof, t_fast, t_menu, t_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Personalizirani Menu", "📈 Napredak"])

# (Profil, Post i Napredak ostaju isti kao u tvojoj zadnjoj verziji...)
with t_prof:
    st.header("Korisnički Profil")
    p_df = load_data(PROFILE_FILE, ["Ime", "Prezime", "Spol", "Tezina", "Visina", "Godine", "Aktivnost", "Cilj"])
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
            st.rerun()

with t_fast:
    st.header("16/8 Timer")
    if 'start_time' not in st.session_state: st.session_state.start_time = None
    if st.button("🚀 Kreni/Završi"):
        if st.session_state.start_time is None: st.session_state.start_time = datetime.datetime.now()
        else:
            dur = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
            save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), pd.DataFrame({"Date": [datetime.date.today()], "Hours": [round(dur, 2)]})]), FAST_FILE)
            st.session_state.start_time = None
            st.rerun()
    if st.session_state.start_time:
        st.metric("Trajanje", f"{(datetime.datetime.now() - st.session_state.start_time).total_seconds()/3600:.2f} h")

# --- KLJUČNI DIO: PAMETNI MENU ---
with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: st.warning("Ispunite profil.")
    else:
        u = p_df.iloc[0]
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        st.info(f"Cilj: {m['kcal']} kcal")

        if st.button("🪄 GENERIRAJ OPTIMIZIRANI MENU"):
            # PAMETNA LOGIKA: Pokušaj 100 puta naći kombinaciju koja ne probija kcal limit
            found = False
            for _ in range(100):
                b = random.choice([x for x in KETO_MEALS if x['type'] == "Breakfast"])
                l = random.choice([x for x in KETO_MEALS if x['type'] == "Lunch"])
                d = random.choice([x for x in KETO_MEALS if x['type'] == "Dinner"])
                s = random.choice([x for x in KETO_MEALS if x['type'] == "Snack"])
                
                total_kcal = b['kcal'] + l['kcal'] + d['kcal'] + s['kcal']
                
                if total_kcal <= m['kcal']:
                    found = True
                    # Prikaz
                    st.subheader("📋 Tvoj sigurni Keto Meni (ispod limita)")
                    for label, meal in [("Doručak", b), ("Ručak", l), ("Večera", d), ("Snack", s)]:
                        with st.expander(f"**{label}: {meal['name']}**", expanded=True):
                            for ing in meal['ingredients']: st.write(f"- {ing}")
                    
                    st.divider()
                    tk, tf, tp, tc = total_kcal, b['fat']+l['fat']+d['fat']+s['fat'], b['prot']+l['prot']+d['prot']+s['prot'], b['carb']+l['carb']+d['carb']+s['carb']
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Kcal", f"{tk}/{m['kcal']}", delta=tk-m['kcal'], delta_color="inverse")
                    c2.metric("Masti", f"{tf}g/{m['fat']}g", delta=tf-m['fat'])
                    c3.metric("Prot", f"{tp}g/{m['prot']}g", delta=tp-m['prot'])
                    c4.metric("UH", f"{tc}g/{m['carb']}g", delta=tc-m['carb'], delta_color="inverse")
                    break
            if not found:
                st.error("Nisam uspio naći kombinaciju ispod limita. Pokušaj ponovno ili povećaj kcal u profilu.")

with t_prog:
    st.header("Napredak")
    w_in = st.number_input("Težina (kg):", key="w_prog")
    if st.button("Spremi"):
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), pd.DataFrame({"Date": [datetime.date.today()], "Weight_kg": [w_in]})]), WEIGHT_FILE)
    w_hist = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_hist.empty: st.line_chart(w_hist.set_index("Date"))
