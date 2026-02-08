import streamlit as st
import datetime
import pandas as pd
import os
import random

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

# --- 2. MASIVNA BAZA OBROKA (Preko 80 recepata) ---
KETO_MEALS = [
    # --- DORUČAK (Breakfast) ---
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, "ingredients": ["3 jaja", "Slanina (50g)", "Avokado (100g)"], "preparation": "Ispecite slaninu i jaja na maslacu."},
    {"name": "Keto Omelet sa špinatom", "type": "Breakfast", "kcal": 420, "fat": 34, "carb": 4, "prot": 24, "ingredients": ["3 jaja", "Špinat (50g)", "Feta sir (30g)"], "preparation": "Umutite i ispecite na tavi."},
    {"name": "Chia puding s kokosom", "type": "Breakfast", "kcal": 350, "fat": 28, "carb": 6, "prot": 12, "ingredients": ["Chia (30g)", "Kokosovo mlijeko"], "preparation": "Hladiti 2h."},
    {"name": "Kuhana jaja i orasi", "type": "Breakfast", "kcal": 310, "fat": 25, "carb": 3, "prot": 18, "ingredients": ["2 jaja", "Orasi (30g)"], "preparation": "Skuhajte jaja."},
    {"name": "Keto palačinke od badema", "type": "Breakfast", "kcal": 480, "fat": 38, "carb": 7, "prot": 20, "ingredients": ["Bademovo brašno", "Krem sir"], "preparation": "Pecite male palačinke."},
    {"name": "Dimljeni losos i krem sir", "type": "Breakfast", "kcal": 390, "fat": 30, "carb": 4, "prot": 26, "ingredients": ["Losos", "Krem sir", "Krastavac"], "preparation": "Složite rolice."},
    {"name": "Tvrdi sir i masline", "type": "Breakfast", "kcal": 450, "fat": 38, "carb": 3, "prot": 22, "ingredients": ["Paški sir (80g)", "Masline"], "preparation": "Narežite."},
    {"name": "Grčki jogurt i bademi", "type": "Breakfast", "kcal": 380, "fat": 32, "carb": 8, "prot": 15, "ingredients": ["Jogurt", "Bademi"], "preparation": "Pomiješajte."},
    {"name": "Tuna i jaja salata", "type": "Breakfast", "kcal": 410, "fat": 30, "carb": 2, "prot": 32, "ingredients": ["Tuna", "2 jaja"], "preparation": "Pomiješajte."},
    {"name": "Keto kruh i maslac", "type": "Breakfast", "kcal": 340, "fat": 28, "carb": 4, "prot": 12, "ingredients": ["Keto kruh", "Maslac"], "preparation": "Tostirajte."},
    {"name": "Zrnati sir i sjemenke", "type": "Breakfast", "kcal": 290, "fat": 20, "carb": 5, "prot": 24, "ingredients": ["Zrnati sir", "Bundevine sjemenke"], "preparation": "Samo poslužite."},
    {"name": "Pršut i mozzarela", "type": "Breakfast", "kcal": 430, "fat": 34, "carb": 2, "prot": 28, "ingredients": ["Pršut", "Mozzarella"], "preparation": "Zamotajte."},
    {"name": "Asparagus i jaja", "type": "Breakfast", "kcal": 370, "fat": 30, "carb": 5, "prot": 18, "ingredients": ["Šparoge", "2 jaja"], "preparation": "Ispecite na tavi."},
    {"name": "Keto smoothie Avokado", "type": "Breakfast", "kcal": 410, "fat": 36, "carb": 6, "prot": 8, "ingredients": ["Avokado", "Bademovo mlijeko"], "preparation": "Izblendajte."},
    {"name": "Salami i Gouda", "type": "Breakfast", "kcal": 490, "fat": 40, "carb": 2, "prot": 25, "ingredients": ["Salama", "Sir"], "preparation": "Narežite."},
    {"name": "Mushroom Omelet", "type": "Breakfast", "kcal": 380, "fat": 30, "carb": 4, "prot": 22, "ingredients": ["3 jaja", "Gljive"], "preparation": "Ispecite."},
    {"name": "Biftek i jaja", "type": "Breakfast", "kcal": 650, "fat": 48, "carb": 0, "prot": 52, "ingredients": ["Mali biftek", "2 jaja"], "preparation": "Ispecite."},
    {"name": "Celer i kikiriki maslac", "type": "Breakfast", "kcal": 320, "fat": 26, "carb": 6, "prot": 10, "ingredients": ["Celer", "Kikiriki maslac"], "preparation": "Namažite."},
    {"name": "Sardine i rikula", "type": "Breakfast", "kcal": 360, "fat": 28, "carb": 1, "prot": 24, "ingredients": ["Sardine", "Rikula"], "preparation": "Poslužite hladno."},
    {"name": "Halloumi na tavi", "type": "Breakfast", "kcal": 440, "fat": 35, "carb": 3, "prot": 26, "ingredients": ["Halloumi", "Ulje"], "preparation": "Pecite 2 min."},

    # --- RUČAK (Lunch) ---
    {"name": "Piletina u curry umaku", "type": "Lunch", "kcal": 610, "fat": 45, "carb": 7, "prot": 42, "ingredients": ["Piletina", "Kokosovo mlijeko", "Curry"], "preparation": "Dinstajte u tavi."},
    {"name": "Bolognese s tikvicama", "type": "Lunch", "kcal": 580, "fat": 42, "carb": 9, "prot": 38, "ingredients": ["Mljeveno meso", "Tikvice", "Umak od rajčice"], "preparation": "Tikvice narežite na špagete."},
    {"name": "Juneći odrezak i brokola", "type": "Lunch", "kcal": 720, "fat": 55, "carb": 5, "prot": 48, "ingredients": ["Junetina", "Brokula", "Maslac"], "preparation": "Brokulu na pari, meso na tavu."},
    {"name": "Salata s piletinom i slaninom", "type": "Lunch", "kcal": 550, "fat": 40, "carb": 4, "prot": 44, "ingredients": ["Piletina", "Slanina", "Zelena salata"], "preparation": "Pomiješajte s maslinovim uljem."},
    {"name": "Svinjska rebra i kupus", "type": "Lunch", "kcal": 850, "fat": 65, "carb": 6, "prot": 50, "ingredients": ["Rebra", "Kupus salata"], "preparation": "Pecite rebra u pećnici."},
    {"name": "Tuna steak i matovilac", "type": "Lunch", "kcal": 480, "fat": 32, "carb": 2, "prot": 45, "ingredients": ["Tuna", "Matovilac", "Limun"], "preparation": "Kratko pecite tunu."},
    {"name": "Sarma bez riže", "type": "Lunch", "kcal": 520, "fat": 38, "carb": 6, "prot": 34, "ingredients": ["Mljeveno meso", "Kupus"], "preparation": "Kuhajte kao klasičnu sarmu."},
    {"name": "Pureći file s parmezanom", "type": "Lunch", "kcal": 590, "fat": 42, "carb": 3, "prot": 48, "ingredients": ["Puretina", "Parmezan", "Maslac"], "preparation": "Pohajte u parmezanu."},
    {"name": "Piletina Alfredo (Zoodles)", "type": "Lunch", "kcal": 640, "fat": 48, "carb": 7, "prot": 42, "ingredients": ["Piletina", "Vrhnje", "Tikvice"], "preparation": "Napravite gusti umak."},
    {"name": "Kobasice i dinstani kupus", "type": "Lunch", "kcal": 710, "fat": 58, "carb": 8, "prot": 36, "ingredients": ["Keto kobasice", "Kiseli kupus"], "preparation": "Sve dinstajte zajedno."},
    {"name": "Pečena patka s povrćem", "type": "Lunch", "kcal": 790, "fat": 62, "carb": 4, "prot": 50, "ingredients": ["Patka", "Povrće niskog UH"], "preparation": "Dugo pecite."},
    {"name": "Teletina pod pekom", "type": "Lunch", "kcal": 680, "fat": 48, "carb": 2, "prot": 55, "ingredients": ["Teletina", "Maslinovo ulje"], "preparation": "Pecite u pećnici."},
    {"name": "Riblji file u škrtocu", "type": "Lunch", "kcal": 420, "fat": 28, "carb": 4, "prot": 38, "ingredients": ["Oslić", "Povrće"], "preparation": "Pecite u papiru za pečenje."},
    {"name": "Juneći gulaš bez krumpira", "type": "Lunch", "kcal": 590, "fat": 42, "carb": 7, "prot": 45, "ingredients": ["Junetina", "Luk", "Začini"], "preparation": "Dugo kuhajte."},
    {"name": "Piletina s pesto umakom", "type": "Lunch", "kcal": 620, "fat": 48, "carb": 5, "prot": 40, "ingredients": ["Piletina", "Pesto", "Pinjoli"], "preparation": "Namažite pesto na piletinu."},
    {"name": "Keto Pizza (Fathead tijesto)", "type": "Lunch", "kcal": 850, "fat": 68, "carb": 9, "prot": 42, "ingredients": ["Sir", "Bademovo brašno", "Dodaci"], "preparation": "Ispecite koru od sira."},
    {"name": "Škampi na buzaru (bez mrvica)", "type": "Lunch", "kcal": 450, "fat": 30, "carb": 5, "prot": 38, "ingredients": ["Škampi", "Vino", "Češnjak"], "preparation": "Brzo dinstajte."},
    {"name": "Salata s pečenom govedinom", "type": "Lunch", "kcal": 510, "fat": 36, "carb": 3, "prot": 42, "ingredients": ["Govedina", "Rikula", "Pinjoli"], "preparation": "Narežite meso tanko."},
    {"name": "Janjetina s ražnja (porcija)", "type": "Lunch", "kcal": 750, "fat": 58, "carb": 0, "prot": 52, "ingredients": ["Janjetina", "Zelena salata"], "preparation": "Poslužite bez priloga."},
    {"name": "Punjene paprike (bez riže)", "type": "Lunch", "kcal": 530, "fat": 39, "carb": 7, "prot": 35, "ingredients": ["Meso", "Paprike"], "preparation": "Pecite u pećnici."},

    # --- VEČERA (Dinner) ---
    {"name": "Ribeye Steak", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 0, "prot": 52, "ingredients": ["Steak", "Maslac"], "preparation": "Pecite na jakoj vatri."},
    {"name": "Tikvice Carbonara", "type": "Dinner", "kcal": 540, "fat": 42, "carb": 9, "prot": 26, "ingredients": ["Tikvice", "Panceta", "Jaja"], "preparation": "Umiješajte žumanjke na kraju."},
    {"name": "Mozzarella i rajčica", "type": "Dinner", "kcal": 380, "fat": 30, "carb": 6, "prot": 22, "ingredients": ["Mozzarella", "Rajčica"], "preparation": "Prelijte uljem."},
    {"name": "Svinjski kotlet", "type": "Dinner", "kcal": 610, "fat": 45, "carb": 1, "prot": 42, "ingredients": ["Kotlet", "Svinjska mast"], "preparation": "Ispecite na tavi."},
    {"name": "Salata od plodova mora", "type": "Dinner", "kcal": 410, "fat": 28, "carb": 4, "prot": 35, "ingredients": ["Dagnje", "Lignje", "Ulje"], "preparation": "Skuhajte i ohladite."},
    {"name": "Omlet s tartufima", "type": "Dinner", "kcal": 460, "fat": 38, "carb": 3, "prot": 24, "ingredients": ["Jaja", "Tartufata"], "preparation": "Lagano ispecite."},
    {"name": "Keto pogačice s čvarcima", "type": "Dinner", "kcal": 520, "fat": 48, "carb": 5, "prot": 18, "ingredients": ["Čvarci", "Jaja", "Sir"], "preparation": "Ispecite u pećnici."},
    {"name": "Pečeni camembert", "type": "Dinner", "kcal": 440, "fat": 36, "carb": 2, "prot": 28, "ingredients": ["Camembert", "Orasi"], "preparation": "Rastopite u pećnici."},
    {"name": "Lignje na žaru", "type": "Dinner", "kcal": 480, "fat": 32, "carb": 5, "prot": 40, "ingredients": ["Lignje", "Tršćanski umak"], "preparation": "Pecite brzo."},
    {"name": "Goveđi carpaccio", "type": "Dinner", "kcal": 350, "fat": 25, "carb": 1, "prot": 30, "ingredients": ["Govedina", "Parmezan"], "preparation": "Poslužite sirovo."},
    {"name": "Piletina u parmezanu", "type": "Dinner", "kcal": 590, "fat": 42, "carb": 3, "prot": 45, "ingredients": ["Piletina", "Parmezan"], "preparation": "Pecite dok ne postane hrskavo."},
    {"name": "Plata: Špek, kulen i sir", "type": "Dinner", "kcal": 650, "fat": 55, "carb": 2, "prot": 38, "ingredients": ["Špek", "Kulen", "Sir"], "preparation": "Samo narežite."},
    {"name": "Pečeni karfiol s čedarom", "type": "Dinner", "kcal": 410, "fat": 32, "carb": 8, "prot": 18, "ingredients": ["Karfiol", "Cheddar sir"], "preparation": "Zapržite u pećnici."},
    {"name": "Srdele na gradelama", "type": "Dinner", "kcal": 390, "fat": 26, "carb": 0, "prot": 36, "ingredients": ["Srdele", "Ulje"], "preparation": "Pecite na žaru."},
    {"name": "Keto tacosi od sira", "type": "Dinner", "kcal": 580, "fat": 45, "carb": 5, "prot": 38, "ingredients": ["Sir (tijesto)", "Meso"], "preparation": "Sir otopite u obliku tacosa."},
    {"name": "Miješano meso (grill)", "type": "Dinner", "kcal": 720, "fat": 52, "carb": 1, "prot": 55, "ingredients": ["Vratina", "Kobasica"], "preparation": "Grilajte."},
    {"name": "Salata Niçoise (Keto)", "type": "Dinner", "kcal": 490, "fat": 38, "carb": 6, "prot": 30, "ingredients": ["Tuna", "Jaja", "Mahune"], "preparation": "Složite salatu."},
    {"name": "Domaća kobasica i senf", "type": "Dinner", "kcal": 620, "fat": 50, "carb": 4, "prot": 32, "ingredients": ["Kobasica", "Domaći senf"], "preparation": "Skuhajte kobasice."},
    {"name": "File oslića na maslacu", "type": "Dinner", "kcal": 430, "fat": 32, "carb": 2, "prot": 35, "ingredients": ["Oslić", "Maslac"], "preparation": "Pecite polako."},
    {"name": "Punjeni šampinjoni", "type": "Dinner", "kcal": 380, "fat": 30, "carb": 5, "prot": 20, "ingredients": ["Gljive", "Sir", "Slanina"], "preparation": "Napunite i pecite."},

    # --- SNACK (Snack) ---
    {"name": "Bademi i orasi", "type": "Snack", "kcal": 190, "fat": 17, "carb": 3, "prot": 6, "ingredients": ["Orašasti plodovi"], "preparation": "Spremno."},
    {"name": "Masline i sir", "type": "Snack", "kcal": 280, "fat": 26, "carb": 3, "prot": 10, "ingredients": ["Masline", "Sir"], "preparation": "Narežite."},
    {"name": "Jaje s majonezom", "type": "Snack", "kcal": 210, "fat": 18, "carb": 1, "prot": 7, "ingredients": ["Jaje", "Majoneza"], "preparation": "Poslužite."},
    {"name": "Čvarci", "type": "Snack", "kcal": 350, "fat": 32, "carb": 0, "prot": 14, "ingredients": ["Čvarci"], "preparation": "Spremno."},
    {"name": "Pecivo od sira", "type": "Snack", "kcal": 220, "fat": 18, "carb": 2, "prot": 12, "ingredients": ["Mozzarella", "Jaje"], "preparation": "Pecite 10 min."},
    {"name": "Keto krekeri (Sjemenke)", "type": "Snack", "kcal": 180, "fat": 15, "carb": 4, "prot": 6, "ingredients": ["Sezam", "Lan"], "preparation": "Sušite u pećnici."},
    {"name": "Šaka lješnjaka", "type": "Snack", "kcal": 170, "fat": 16, "carb": 2, "prot": 4, "ingredients": ["Lješnjaci"], "preparation": "Spremno."},
    {"name": "Kockica tamne čokolade (90%)", "type": "Snack", "kcal": 120, "fat": 10, "carb": 3, "prot": 2, "ingredients": ["Tamna čokolada"], "preparation": "Spremno."},
    {"name": "Avokado s limunom", "type": "Snack", "kcal": 240, "fat": 22, "carb": 3, "prot": 2, "ingredients": ["Avokado"], "preparation": "Samo prepolovite."},
    {"name": "Beef Jerky", "type": "Snack", "kcal": 150, "fat": 6, "carb": 2, "prot": 22, "ingredients": ["Sušena govedina"], "preparation": "Spremno."},
    {"name": "Krastavci sa vrhnjem", "type": "Snack", "kcal": 140, "fat": 12, "carb": 4, "prot": 3, "ingredients": ["Krastavac", "Vrhnje"], "preparation": "Narežite."},
    {"name": "Pečeni lješnjaci", "type": "Snack", "kcal": 180, "fat": 17, "carb": 3, "prot": 4, "ingredients": ["Lješnjaci"], "preparation": "Tostirajte."},
    {"name": "Parmezan čips", "type": "Snack", "kcal": 190, "fat": 14, "carb": 1, "prot": 15, "ingredients": ["Parmezan"], "preparation": "Ispecite hrpice sira."},
    {"name": "Rolice šunke i sira", "type": "Snack", "kcal": 210, "fat": 16, "carb": 2, "prot": 14, "ingredients": ["Šunka", "Sir"], "preparation": "Zarolajte."},
    {"name": "Chia jogurt", "type": "Snack", "kcal": 220, "fat": 18, "carb": 5, "prot": 8, "ingredients": ["Chia", "Jogurt"], "preparation": "Namočite."},
    {"name": "Maslac od badema (žlica)", "type": "Snack", "kcal": 100, "fat": 9, "carb": 2, "prot": 4, "ingredients": ["Bademov maslac"], "preparation": "Spremno."},
    {"name": "Kokos čips", "type": "Snack", "kcal": 150, "fat": 14, "carb": 3, "prot": 1, "ingredients": ["Kokos listići"], "preparation": "Spremno."},
    {"name": "Sjemenke suncokreta", "type": "Snack", "kcal": 160, "fat": 14, "carb": 4, "prot": 6, "ingredients": ["Suncokret"], "preparation": "Spremno."},
    {"name": "Brazilski orah (2 kom)", "type": "Snack", "kcal": 70, "fat": 7, "carb": 1, "prot": 1, "ingredients": ["Brazilski orah"], "preparation": "Spremno."},
    {"name": "Kuglice od sira i začina", "type": "Snack", "kcal": 230, "fat": 20, "carb": 2, "prot": 10, "ingredients": ["Krem sir", "Vlasac"], "preparation": "Oblikujte kuglice."},
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

# --- 4. APLIKACIJA ---
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

with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: 
        st.warning("Prvo ispunite profil.")
    else:
        u = p_df.iloc[0]
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        
        st.subheader(f"🎯 Cilj: {m['kcal']} kcal")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Masti", f"{m['fat']}g")
        m2.metric("Proteini", f"{m['prot']}g")
        m3.metric("Ugljikohidrati", f"{m['carb']}g")
        m4.write("*(70/25/5)*")
        
        st.divider()

        if st.button("🪄 GENERIRAJ OPTIMALNI MENU", use_container_width=True):
            combos = []
            # Razdvajanje lista po tipovima da izbjegnemo grešku
            b_list = [x for x in KETO_MEALS if x['type'] == "Breakfast"]
            l_list = [x for x in KETO_MEALS if x['type'] == "Lunch"]
            d_list = [x for x in KETO_MEALS if x['type'] == "Dinner"]
            s_list = [x for x in KETO_MEALS if x['type'] == "Snack"]

            for _ in range(1000):
                b = random.choice(b_list)
                l = random.choice(l_list)
                d = random.choice(d_list)
                s = random.choice(s_list)
                tk = b['kcal'] + l['kcal'] + d['kcal'] + s['kcal']
                combos.append({"meals": [b, l, d, s], "total_kcal": tk, "diff": abs(tk - m['kcal'])})
            
            best = min(combos, key=lambda x: x['diff'])
            
            st.success(f"Pronađen meni od {best['total_kcal']} kcal!")
            
            labels = ["Doručak", "Ručak", "Večera", "Snack"]
            for i, meal in enumerate(best['meals']):
                with st.expander(f"{labels[i]}: {meal['name']} ({meal['kcal']} kcal)", expanded=True):
                    st.write(f"**Sastojci:** {', '.join(meal['ingredients'])}")
                    st.info(f"**Upute:** {meal['preparation']}")

            # FIKSNA PIĆA ISPOD SVIH MENIJA
            st.warning("☕ **Pića (Dozvoljeno uz svaki obrok):** Voda, nezaslađeni čaj, crna kava.")

            st.divider()
            tk, tf, tp, tc = best['total_kcal'], sum(x['fat'] for x in best['meals']), sum(x['prot'] for x in best['meals']), sum(x['carb'] for x in best['meals'])
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Kcal", f"{tk}", delta=tk-m['kcal'], delta_color="inverse")
            res2.metric("Masti", f"{tf}g", delta=tf-m['fat'])
            res3.metric("Prot", f"{tp}g", delta=tp-m['prot'])
            res4.metric("UH", f"{tc}g", delta=tc-m['carb'], delta_color="inverse")
