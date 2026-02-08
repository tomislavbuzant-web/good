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

# --- 2. BAZA OBROKA S PRIPREMOM I MAKSOSIMA ---
KETO_MEALS = [
    # DORUČAK
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, 
     "ingredients": ["3 jaja (150g)", "Slanina (50g)", "Avokado (100g)", "Maslac (10g)"],
     "preparation": "Ispecite slaninu na tavi dok ne postane hrskava. Na istoj masnoći ispecite jaja. Poslužite uz narezani avokado."},
    {"name": "Keto Omelet sa špinatom", "type": "Breakfast", "kcal": 420, "fat": 34, "carb": 4, "prot": 24, 
     "ingredients": ["3 jaja (150g)", "Špinat (50g)", "Feta sir (30g)", "Maslinovo ulje (10ml)"],
     "preparation": "Umutite jaja, dodajte špinat i fetu. Pecite na laganoj vatri dok se sir ne otopi."},
    {"name": "Chia puding s kokosom", "type": "Breakfast", "kcal": 350, "fat": 28, "carb": 6, "prot": 12, 
     "ingredients": ["Chia sjemenke (30g)", "Kokosovo mlijeko (150ml)", "Bademi (10g)"],
     "preparation": "Pomiješajte chia sjemenke i mlijeko. Ostavite u hladnjaku preko noći. Pospite bademima prije konzumacije."},

    # RUČAK
    {"name": "Losos s pečenim šparogama", "type": "Lunch", "kcal": 620, "fat": 42, "carb": 6, "prot": 45, 
     "ingredients": ["Filet lososa (200g)", "Šparoge (150g)", "Maslinovo ulje (20ml)", "Zelena salata (100g)"],
     "preparation": "Losos i šparoge pecite u pećnici 15 min na 200°C. Prelijte maslinovim uljem i poslužite uz salatu."},
    {"name": "Piletina u vrhnju i gljivama", "type": "Lunch", "kcal": 680, "fat": 50, "carb": 8, "prot": 44, 
     "ingredients": ["Pileći zabatak (220g)", "Šampinjoni (100g)", "Vrhnje (60ml)", "Rikula (50g)"],
     "preparation": "Piletinu narežite na kockice i prepecite. Dodajte gljive, a na kraju vrhnje. Kratko prokuhajte."},
    {"name": "Juneći burger bez peciva", "type": "Lunch", "kcal": 700, "fat": 55, "carb": 5, "prot": 40, 
     "ingredients": ["Junetina (200g)", "Cheddar (25g)", "Avokado (50g)", "Miješana salata (150g)"],
     "preparation": "Oblikujte pljeskavicu i ispecite. Zadnju minutu stavite sir na meso. Poslužite na posteljici od salate s avokadom."},

    # VEČERA
    {"name": "Ribeye Steak s maslacem", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 2, "prot": 52, 
     "ingredients": ["Ribeye odrezak (250g)", "Maslac (25g)", "Zelena salata (100g)"],
     "preparation": "Odrezak pecite na jakoj vatri 3-4 minute sa svake strane. Na topli meso stavite kocku maslaca."},
    {"name": "Tikvice Carbonara", "type": "Dinner", "kcal": 540, "fat": 42, "carb": 9, "prot": 26, 
     "ingredients": ["Tikvice (250g)", "Panceta (60g)", "2 žumanjka", "Parmezan (20g)"],
     "preparation": "Prepecite pancetu. Dodajte 'špagete' od tikvica na 2 min. Maknite s vatre i umiješajte smjesu žumanjaka i parmezana."},
    {"name": "Svinjski kotlet s kupusom", "type": "Dinner", "kcal": 610, "fat": 45, "carb": 6, "prot": 42, 
     "ingredients": ["Svinjski kotlet (200g)", "Svinjska mast (15g)", "Svježi kupus (200g)"],
     "preparation": "Kotlet ispecite na masti. Kupus narežite tanko i začinite uljem i octom."},

    # SNACK
    {"name": "Orašasti plodovi", "type": "Snack", "kcal": 210, "fat": 19, "carb": 4, "prot": 6, 
     "ingredients": ["Orasi i bademi (30g)"],
     "preparation": "Spremno za konzumaciju."},
    {"name": "Masline i sir", "type": "Snack", "kcal": 280, "fat": 26, "carb": 3, "prot": 10, 
     "ingredients": ["Masline (50g)", "Tvrdi sir (40g)"],
     "preparation": "Narežite sir na kockice i poslužite uz masline."}
]

# --- 3. LOGIKA ---
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

# (Profil, Post i Napredak ostaju isti radi stabilnosti)
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

# --- MENU TAB ---
with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: st.warning("Ispunite profil.")
    else:
        u = p_df.iloc[0]
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        st.info(f"Osobni limit: {m['kcal']} kcal | Ciljni makrosi: M:{m['fat']}g, P:{m['prot']}g, UH:{m['carb']}g")

        if st.button("🪄 GENERIRAJ OPTIMIZIRANI MENU", use_container_width=True):
            found = False
            for _ in range(200): # Povećan broj pokušaja zbog strožih uvjeta
                b = random.choice([x for x in KETO_MEALS if x['type'] == "Breakfast"])
                l = random.choice([x for x in KETO_MEALS if x['type'] == "Lunch"])
                d = random.choice([x for x in KETO_MEALS if x['type'] == "Dinner"])
                s = random.choice([x for x in KETO_MEALS if x['type'] == "Snack"])
                
                tk = b['kcal'] + l['kcal'] + d['kcal'] + s['kcal']
                
                if tk <= m['kcal']:
                    found = True
                    st.subheader("📋 Tvoj Dnevni Meni")
                    
                    for label, meal in [("Doručak", b), ("Ručak", l), ("Večera", d), ("Snack", s)]:
                        # Naslov s makrosima, expander je zatvoren (expanded=False)
                        header_text = f"{label}: {meal['name']} | 🔥 {meal['kcal']} kcal (M:{meal['fat']}g, P:{meal['prot']}g, UH:{meal['carb']}g)"
                        with st.expander(header_text, expanded=False):
                            st.write("**🛒 Namirnice:**")
                            for ing in meal['ingredients']: st.write(f"- {ing}")
                            st.write("**👨‍🍳 Priprema:**")
                            st.info(meal['preparation'])
                    
                    st.divider()
                    tf, tp, tc = b['fat']+l['fat']+d['fat']+s['fat'], b['prot']+l['prot']+d['prot']+s['prot'], b['carb']+l['carb']+d['carb']+s['carb']
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Ukupno Kcal", f"{tk}/{m['kcal']}", delta=tk-m['kcal'], delta_color="inverse")
                    c2.metric("Masti", f"{tf}g/{m['fat']}g", delta=tf-m['fat'])
                    c3.metric("Prot", f"{tp}g/{m['prot']}g", delta=tp-m['prot'])
                    c4.metric("UH", f"{tc}g/{m['carb']}g", delta=tc-m['carb'], delta_color="inverse")
                    break
            if not found:
                st.error("Nisam pronašao kombinaciju ispod vašeg kalorijskog limita. Pokušajte ponovno.")

with t_prog:
    st.header("Napredak")
    w_in = st.number_input("Težina (kg):", key="w_prog")
    if st.button("Spremi"):
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), pd.DataFrame({"Date": [datetime.date.today()], "Weight_kg": [w_in]})]), WEIGHT_FILE)
    w_hist = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_hist.empty: st.line_chart(w_hist.set_index("Date"))
