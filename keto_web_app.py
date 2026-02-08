import streamlit as st
import datetime
import pandas as pd
import os
import random
import plotly.express as px

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

PROFILE_FILE = "user_profile.csv"
FAST_FILE = "fasting_history.csv"

def save_data(df, filename): df.to_csv(filename, index=False)
def load_data(filename, columns):
    if os.path.exists(filename):
        try: return pd.read_csv(filename)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- 2. BAZA (Ovdje ubaci onih 80 recepata koje sam ti poslao prošli put) ---
KETO_MEALS = [
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, "ingredients": ["3 jaja", "Slanina (50g)", "Avokado (100g)"], "preparation": "Pecite slaninu i jaja na maslacu."},
    # ... Ovdje idu svi ostali recepti (Ručak, Večera, Snack) ...
    {"name": "Piletina u curry umaku", "type": "Lunch", "kcal": 610, "fat": 45, "carb": 7, "prot": 42, "ingredients": ["Piletina", "Kokosovo mlijeko"], "preparation": "Dinstajte na laganoj vatri."},
    {"name": "Ribeye Steak", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 0, "prot": 52, "ingredients": ["Steak", "Maslac"], "preparation": "Pecite na jakoj vatri."},
    {"name": "Bademi i orasi", "type": "Snack", "kcal": 190, "fat": 17, "carb": 3, "prot": 6, "ingredients": ["Orašasti plodovi"], "preparation": "Spremno za jelo."}
]

# --- 3. POMOĆNE FUNKCIJE ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    bmr = (10 * tezina + 6.25 * visina - 5 * godine + 5) if spol == "Muško" else (10 * tezina + 6.25 * visina - 5 * godine - 161)
    act_mult = {"Sjedilački": 1.2, "Lagano": 1.375, "Umjereno": 1.55, "Vrlo aktivno": 1.725}
    tdee = bmr * act_mult[aktivnost]
    if cilj == "Gubitak masti": target_kcal = tdee * 0.8
    elif cilj == "Dobivanje mišića": target_kcal = tdee * 1.1
    else: target_kcal = tdee
    return {"kcal": int(target_kcal), "fat": int((target_kcal * 0.7) / 9), "prot": int((target_kcal * 0.25) / 4), "carb": int((target_kcal * 0.05) / 4)}

# --- 4. TABS ---
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
        if st.form_submit_button("Spremi Profil"):
            save_data(pd.DataFrame([{"Ime": ime, "Spol": spol, "Tezina": tezina, "Visina": visina, "Godine": godine, "Aktivnost": aktivnost, "Cilj": cilj}]), PROFILE_FILE)
            st.success("Profil spremljen!")

with t_fast:
    st.header("Intermittent Fasting")
    
    st.write("Prati svoje razdoblje posta.")
    start_date = st.date_input("Datum početka", datetime.date.today())
    start_time = st.time_input("Vrijeme zadnjeg obroka", datetime.time(20, 0))
    
    if st.button("Završi post i spremi"):
        now = datetime.datetime.now()
        start_dt = datetime.datetime.combine(start_date, start_time)
        diff = now - start_dt
        hours = round(diff.total_seconds() / 3600, 1)
        
        f_df = load_data(FAST_FILE, ["Datum", "Sati"])
        new_f = pd.DataFrame([{"Datum": now.strftime("%Y-%m-%d"), "Sati": hours}])
        save_data(pd.concat([f_df, new_f]), FAST_FILE)
        st.success(f"Bravo! Postili ste {hours} sati.")

with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: 
        st.warning("Prvo ispunite profil u prvom tabu.")
    else:
        u = p_df.iloc[0]
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        
        st.subheader(f"Dnevni cilj: {m['kcal']} kcal")
        
        if st.button("🪄 GENERIRAJ NOVI DNEVNI PLAN"):
            # Logika odabira...
            b_list = [x for x in KETO_MEALS if x['type'] == "Breakfast"]
            l_list = [x for x in KETO_MEALS if x['type'] == "Lunch"]
            d_list = [x for x in KETO_MEALS if x['type'] == "Dinner"]
            s_list = [x for x in KETO_MEALS if x['type'] == "Snack"]
            
            # Nasumičan odabir za primjer
            plan = [random.choice(b_list), random.choice(l_list), random.choice(d_list), random.choice(s_list)]
            
            for item in plan:
                with st.expander(f"{item['type']}: {item['name']} ({item['kcal']} kcal)"):
                    st.write(f"**Sastojci:** {', '.join(item['ingredients'])}")
                    st.info(f"**Priprema:** {item['preparation']}")

with t_prog:
    st.header("Tvoj Napredak")
    f_df = load_data(FAST_FILE, ["Datum", "Sati"])
    if not f_df.empty:
        fig = px.area(f_df, x="Datum", y="Sati", title="Sati posta kroz vrijeme", color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Podaci će se pojaviti ovdje nakon što prvi put spremite post.")
