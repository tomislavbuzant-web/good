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

# --- 2. BAZA OBROKA ---
KETO_MEALS = [
    # DORUČAK
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, "ingredients": ["3 jaja", "Slanina (50g)", "Avokado (100g)"], "preparation": "Ispecite slaninu i jaja, poslužite s avokadom."},
    {"name": "Keto Omelet sa špinatom", "type": "Breakfast", "kcal": 420, "fat": 34, "carb": 4, "prot": 24, "ingredients": ["3 jaja", "Špinat (50g)", "Feta (30g)"], "preparation": "Umutite jaja sa špinatom i sirom te ispecite."},
    {"name": "Brzi doručak: Kuhana jaja i orasi", "type": "Breakfast", "kcal": 310, "fat": 25, "carb": 3, "prot": 18, "ingredients": ["2 jaja", "Orasi (30g)"], "preparation": "Skuhajte jaja i poslužite uz orahe."},
    
    # RUČAK
    {"name": "Losos s pečenim šparogama", "type": "Lunch", "kcal": 620, "fat": 42, "carb": 6, "prot": 45, "ingredients": ["Losos (200g)", "Šparoge (150g)", "Maslinovo ulje"], "preparation": "Pecite losos i šparoge u pećnici 15 min na 200°C."},
    {"name": "Piletina u vrhnju", "type": "Lunch", "kcal": 680, "fat": 50, "carb": 8, "prot": 44, "ingredients": ["Pileći zabatak (220g)", "Vrhnje (60ml)", "Rikula"], "preparation": "Piletinu ispecite i prelijte vrhnjem."},
    {"name": "Bijela riba na lešo s blitvom", "type": "Lunch", "kcal": 410, "fat": 28, "carb": 5, "prot": 35, "ingredients": ["Oslić (200g)", "Blitva (200g)", "Puno maslinovog ulja"], "preparation": "Skuhajte ribu i blitvu, obilno zalijte maslinovim uljem."},
    {"name": "Keto Cezar Salata", "type": "Lunch", "kcal": 550, "fat": 40, "carb": 6, "prot": 38, "ingredients": ["Piletina (150g)", "Zelena salata (200g)", "Parmezan", "Dresing"], "preparation": "Pomiješajte piletinu, salatu i masni dresing."},

    # VEČERA
    {"name": "Ribeye Steak s maslacem", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 2, "prot": 52, "ingredients": ["Ribeye (250g)", "Maslac (25g)", "Zelena salata"], "preparation": "Ispecite steak i na kraju dodajte maslac."},
    {"name": "Tikvice Carbonara", "type": "Dinner", "kcal": 540, "fat": 42, "carb": 9, "prot": 26, "ingredients": ["Tikvice (250g)", "Panceta", "2 žumanjka"], "preparation": "Spiralizirane tikvice pomiješajte s prženom pancetom i žumanjcima."},
    {"name": "Lagana večera: Mozzarella i rajčica", "type": "Dinner", "kcal": 380, "fat": 30, "carb": 6, "prot": 22, "ingredients": ["Mozzarella (125g)", "Rajčica (100g)", "Maslinovo ulje"], "preparation": "Narežite i prelijte maslinovim uljem."},
    {"name": "Svinjski kotlet i kupus", "type": "Dinner", "kcal": 610, "fat": 45, "carb": 6, "prot": 42, "ingredients": ["Kotlet", "Kupus salata (200g)"], "preparation": "Ispecite kotlet i poslužite uz začinjeni kupus."},

    # SNACK
    {"name": "Šaka badema", "type": "Snack", "kcal": 180, "fat": 16, "carb": 3, "prot": 6, "ingredients": ["Bademi (30g)"], "preparation": "Spremno odmah."},
    {"name": "Masline i sir", "type": "Snack", "kcal": 280, "fat": 26, "carb": 3, "prot": 10, "ingredients": ["Masline (50g)", "Sir (40g)"], "preparation": "Narežite i poslužite."},
    {"name": "Bez snacka", "type": "Snack", "kcal": 0, "fat": 0, "carb": 0, "prot": 0, "ingredients": ["Voda ili crna kava"], "preparation": "Postite do idućeg obroka."}
]

# --- 3. LOGIKA IZRAČUNA ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    bmr = (10 * tezina + 6.25 * visina - 5 * godine + 5) if spol == "Muško" else (10 * tezina + 6.25 * visina - 5 * godine - 161)
    act_mult = {"Sjedilački": 1.2, "Lagano": 1.375, "Umjereno": 1.55, "Vrlo aktivno": 1.725}
    tdee = bmr * act_mult[aktivnost]
    if cilj == "Gubitak masti": target_kcal = tdee * 0.8
    elif cilj == "Dobivanje mišića": target_kcal = tdee * 1.1
    else: target_kcal = tdee
    return {"kcal": int(target_kcal), "fat": int((target_kcal * 0.7) / 9), "prot": int((target_kcal * 0.25) / 4), "carb": int((target_kcal * 0.05) / 4)}

# --- 4. APP INTERFEJS ---
t_prof, t_fast, t_menu, t_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Personalizirani Menu", "📈 Napredak"])

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
    st.header("Fast Timer")
    if 'start_time' not in st.session_state: st.session_state.start_time = None
    if st.button("🚀 Start/Stop"):
        if st.session_state.start_time is None: st.session_state.start_time = datetime.datetime.now()
        else:
            dur = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
            save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), pd.DataFrame({"Date": [datetime.date.today()], "Hours": [round(dur, 2)]})]), FAST_FILE)
            st.session_state.start_time = None
            st.rerun()
    if st.session_state.start_time:
        st.metric("Vrijeme", f"{(datetime.datetime.now() - st.session_state.start_time).total_seconds()/3600:.2f} h")

# --- PAMETNA LOGIKA GENERIRANJA ---
with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: st.warning("Ispunite profil.")
    else:
        u = p_df.iloc[0]
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        
        if st.button("🪄 GENERIRAJ OPTIMALNI MENU", use_container_width=True):
            combos = []
            for _ in range(500):
                b = random.choice([x for x in KETO_MEALS if x['type'] == "Breakfast"])
                l = random.choice([x for x in KETO_MEALS if x['type'] == "Lunch"])
                d = random.choice([x for x in KETO_MEALS if x['type'] == "Dinner"])
                s = random.choice([x for x in KETO_MEALS if x['type'] == "Snack"])
                
                tk = b['kcal'] + l['kcal'] + d['kcal'] + s['kcal']
                # Pohranjujemo kombinaciju i njezinu apsolutnu razliku od cilja
                combos.append({
                    "meals": [b, l, d, s],
                    "total_kcal": tk,
                    "diff": abs(tk - m['kcal'])
                })
            
            # Sortiramo po razlici i uzimamo najbolju (najbližu limitu)
            best = min(combos, key=lambda x: x['diff'])
            
            st.subheader("📋 Preporučeni Meni (Najbolje usklađen)")
            labels = ["Doručak", "Ručak", "Večera", "Snack"]
            for i, meal in enumerate(best['meals']):
                header = f"{labels[i]}: {meal['name']} | 🔥 {meal['kcal']} kcal (M:{meal['fat']}g, P:{meal['prot']}g, UH:{meal['carb']}g)"
                with st.expander(header, expanded=False):
                    st.write("**🛒 Namirnice:**")
                    for ing in meal['ingredients']: st.write(f"- {ing}")
                    st.info(f"**👨‍🍳 Priprema:** {meal['preparation']}")
            
            st.divider()
            tk = best['total_kcal']
            tf = sum(x['fat'] for x in best['meals'])
            tp = sum(x['prot'] for x in best['meals'])
            tc = sum(x['carb'] for x in best['meals'])
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Kcal", f"{tk}/{m['kcal']}", delta=tk-m['kcal'], delta_color="inverse")
            c2.metric("Masti", f"{tf}g/{m['fat']}g", delta=tf-m['fat'])
            c3.metric("Prot", f"{tp}g/{m['prot']}g", delta=tp-m['prot'])
            c4.metric("UH", f"{tc}g/{m['carb']}g", delta=tc-m['carb'], delta_color="inverse")

with t_prog:
    st.header("Napredak")
    w_hist = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_hist.empty: st.line_chart(w_hist.set_index("Date"))
