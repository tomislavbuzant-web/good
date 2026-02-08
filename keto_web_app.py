import streamlit as st
import datetime
import pandas as pd
import os
import random
import plotly.express as px

# --- 1. POSTAVKE APLIKACIJE ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# Datoteke za spremanje podataka
PROFILE_FILE = "user_profile.csv"
FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"

# --- POPRAVLJENA FUNKCIJA ZA UČITAVANJE ---
def load_data(filename, columns):
    """
    Učitava CSV. Ako datoteka ne postoji, ili ako je oštećena/stara
    pa joj fale stupci, vraća praznu tablicu s ispravnim stupcima.
    """
    if not os.path.exists(filename):
        return pd.DataFrame(columns=columns)
    
    try:
        df = pd.read_csv(filename)
        # PROVJERA: Sadrži li datoteka sve potrebne stupce?
        if not set(columns).issubset(df.columns):
            # Ako fale stupci (npr. stara verzija), vrati praznu tablicu
            return pd.DataFrame(columns=columns)
        return df
    except:
        # U slučaju bilo kakve druge greške pri čitanju
        return pd.DataFrame(columns=columns)

def save_data(df, filename): 
    df.to_csv(filename, index=False)

# --- 2. KOMPLETNA BAZA KETO RECEPATA (80 recepata) ---
KETO_MEALS = [
    # --- DORUČAK ---
    {"name": "Jaja sa slaninom i avokadom", "type": "Breakfast", "kcal": 550, "fat": 45, "carb": 5, "prot": 25, "ingredients": ["3 jaja", "Slanina (50g)", "Avokado"], "preparation": "Ispecite slaninu i jaja."},
    {"name": "Keto Omelet sa špinatom", "type": "Breakfast", "kcal": 420, "fat": 34, "carb": 4, "prot": 24, "ingredients": ["3 jaja", "Špinat", "Feta sir"], "preparation": "Umutite i ispecite."},
    {"name": "Chia puding s kokosom", "type": "Breakfast", "kcal": 350, "fat": 28, "carb": 6, "prot": 12, "ingredients": ["Chia sjemenke", "Kokosovo mlijeko"], "preparation": "Hladiti preko noći."},
    {"name": "Kuhana jaja i orasi", "type": "Breakfast", "kcal": 310, "fat": 25, "carb": 3, "prot": 18, "ingredients": ["2 jaja", "Orasi (30g)"], "preparation": "Skuhajte jaja, poslužite s orasima."},
    {"name": "Keto palačinke", "type": "Breakfast", "kcal": 480, "fat": 38, "carb": 7, "prot": 20, "ingredients": ["Bademovo brašno", "Jaja", "Krem sir"], "preparation": "Pecite male palačinke."},
    {"name": "Dimljeni losos i krem sir", "type": "Breakfast", "kcal": 390, "fat": 30, "carb": 4, "prot": 26, "ingredients": ["Losos", "Krem sir"], "preparation": "Poslužite hladno."},
    {"name": "Paški sir i masline", "type": "Breakfast", "kcal": 450, "fat": 38, "carb": 3, "prot": 22, "ingredients": ["Tvrdi sir", "Masline"], "preparation": "Narežite na kockice."},
    {"name": "Grčki jogurt i bademi", "type": "Breakfast", "kcal": 380, "fat": 32, "carb": 8, "prot": 15, "ingredients": ["Punomasni jogurt", "Bademi"], "preparation": "Pomiješajte."},
    {"name": "Tuna salata s jajima", "type": "Breakfast", "kcal": 410, "fat": 30, "carb": 2, "prot": 32, "ingredients": ["Tuna", "2 jaja", "Majoneza"], "preparation": "Pomiješajte sve sastojke."},
    {"name": "Keto tost s maslacem", "type": "Breakfast", "kcal": 340, "fat": 28, "carb": 4, "prot": 12, "ingredients": ["Keto kruh", "Maslac"], "preparation": "Tostirajte i namažite."},
    {"name": "Zrnati sir i sjemenke", "type": "Breakfast", "kcal": 290, "fat": 20, "carb": 5, "prot": 24, "ingredients": ["Zrnati sir", "Bučine sjemenke"], "preparation": "Pomiješajte."},
    {"name": "Pršut i mozzarela", "type": "Breakfast", "kcal": 430, "fat": 34, "carb": 2, "prot": 28, "ingredients": ["Pršut", "Mozzarella"], "preparation": "Složite na tanjur."},
    {"name": "Šparoge i pečena jaja", "type": "Breakfast", "kcal": 370, "fat": 30, "carb": 5, "prot": 18, "ingredients": ["Šparoge", "2 jaja", "Maslac"], "preparation": "Ispecite šparoge pa dodajte jaja."},
    {"name": "Keto smoothie (Avokado)", "type": "Breakfast", "kcal": 410, "fat": 36, "carb": 6, "prot": 8, "ingredients": ["Avokado", "Bademovo mlijeko", "Kakao"], "preparation": "Izblendajte."},
    {"name": "Zimska salama i sir", "type": "Breakfast", "kcal": 490, "fat": 40, "carb": 2, "prot": 25, "ingredients": ["Salama", "Gouda sir"], "preparation": "Narežite."},
    {"name": "Omlet s gljivama", "type": "Breakfast", "kcal": 380, "fat": 30, "carb": 4, "prot": 22, "ingredients": ["3 jaja", "Šampinjoni"], "preparation": "Dinstajte gljive pa dodajte jaja."},
    {"name": "Biftek i jaja", "type": "Breakfast", "kcal": 650, "fat": 48, "carb": 0, "prot": 52, "ingredients": ["Mali biftek", "2 jaja"], "preparation": "Ispecite meso i jaja na tavi."},
    {"name": "Celer i maslac od kikirikija", "type": "Breakfast", "kcal": 320, "fat": 26, "carb": 6, "prot": 10, "ingredients": ["Celer stabljike", "Kikiriki maslac"], "preparation": "Namažite."},
    {"name": "Sardine s rikulom", "type": "Breakfast", "kcal": 360, "fat": 28, "carb": 1, "prot": 24, "ingredients": ["Sardine u ulju", "Rikula"], "preparation": "Ocijedite i poslužite."},
    {"name": "Halloumi sir na žaru", "type": "Breakfast", "kcal": 440, "fat": 35, "carb": 3, "prot": 26, "ingredients": ["Halloumi", "Maslinovo ulje"], "preparation": "Pecite dok ne porumeni."},

    # --- RUČAK ---
    {"name": "Piletina Curry (Keto)", "type": "Lunch", "kcal": 610, "fat": 45, "carb": 7, "prot": 42, "ingredients": ["Piletina", "Kokosovo mlijeko", "Curry"], "preparation": "Dinstajte piletinu u umaku."},
    {"name": "Tikvice Bolognese", "type": "Lunch", "kcal": 580, "fat": 42, "carb": 9, "prot": 38, "ingredients": ["Mljeveno meso", "Tikvice", "Rajčica"], "preparation": "Umak preko rezanih tikvica."},
    {"name": "Odrezak s brokulom", "type": "Lunch", "kcal": 720, "fat": 55, "carb": 5, "prot": 48, "ingredients": ["Juneći odrezak", "Brokula", "Maslac"], "preparation": "Ispecite meso, brokulu na paru."},
    {"name": "Cezar salata (bez krutona)", "type": "Lunch", "kcal": 550, "fat": 40, "carb": 4, "prot": 44, "ingredients": ["Piletina", "Zelena salata", "Parmezan"], "preparation": "Pomiješajte s dresingom."},
    {"name": "Pečena svinjska rebra", "type": "Lunch", "kcal": 850, "fat": 65, "carb": 6, "prot": 50, "ingredients": ["Rebra", "Kupus salata"], "preparation": "Pecite u pećnici 2h."},
    {"name": "Tuna steak i blitva", "type": "Lunch", "kcal": 480, "fat": 32, "carb": 2, "prot": 45, "ingredients": ["Tuna", "Blitva", "Češnjak"], "preparation": "Kratko ispecite tunu."},
    {"name": "Sarma bez riže", "type": "Lunch", "kcal": 520, "fat": 38, "carb": 6, "prot": 34, "ingredients": ["Mljeveno meso", "Kiseli kupus"], "preparation": "Kuhajte 2h."},
    {"name": "Pohana piletina (bademi)", "type": "Lunch", "kcal": 590, "fat": 42, "carb": 3, "prot": 48, "ingredients": ["Piletina", "Mljeveni bademi", "Jaja"], "preparation": "Pohajte u bademovom brašnu."},
    {"name": "Piletina u vrhnju", "type": "Lunch", "kcal": 640, "fat": 48, "carb": 7, "prot": 42, "ingredients": ["Piletina", "Vrhnje za kuhanje", "Začini"], "preparation": "Dinstajte dok ne zgusne."},
    {"name": "Kobasice i kiseli kupus", "type": "Lunch", "kcal": 710, "fat": 58, "carb": 8, "prot": 36, "ingredients": ["Keto kobasice", "Kiseli kupus"], "preparation": "Kuhajte ili pecite."},
    {"name": "Pečena patka", "type": "Lunch", "kcal": 790, "fat": 62, "carb": 4, "prot": 50, "ingredients": ["Patka batak/zabatak", "Salata"], "preparation": "Pecite dok koža nije hrskava."},
    {"name": "Teletina ispod peke (stil)", "type": "Lunch", "kcal": 680, "fat": 48, "carb": 2, "prot": 55, "ingredients": ["Teletina", "Tikvice", "Patlidžan"], "preparation": "Pecite poklopljeno u pećnici."},
    {"name": "Riba u škartocu", "type": "Lunch", "kcal": 420, "fat": 28, "carb": 4, "prot": 38, "ingredients": ["Bijela riba", "Maslinovo ulje", "Povrće"], "preparation": "Pecite u papiru."},
    {"name": "Keto Gulaš", "type": "Lunch", "kcal": 590, "fat": 42, "carb": 7, "prot": 45, "ingredients": ["Junetina kocke", "Luk", "Voda"], "preparation": "Dugo kuhajte na lagano."},
    {"name": "Piletina Pesto", "type": "Lunch", "kcal": 620, "fat": 48, "carb": 5, "prot": 40, "ingredients": ["Piletina", "Zeleni pesto", "Mozzarella"], "preparation": "Zapecite u pećnici."},
    {"name": "Keto Pizza (podloga sir)", "type": "Lunch", "kcal": 850, "fat": 68, "carb": 9, "prot": 42, "ingredients": ["Mozzarella", "Bademovo brašno", "Salama"], "preparation": "Napravite tijesto od sira i jaja."},
    {"name": "Škampi na buzaru", "type": "Lunch", "kcal": 450, "fat": 30, "carb": 5, "prot": 38, "ingredients": ["Škampi", "Maslinovo ulje", "Češnjak"], "preparation": "Dinstajte na ulju i vinu."},
    {"name": "Salata s govedinom", "type": "Lunch", "kcal": 510, "fat": 36, "carb": 3, "prot": 42, "ingredients": ["Hladna govedina", "Rikula", "Ulje"], "preparation": "Narežite meso na trakice."},
    {"name": "Janjetina i mladi luk", "type": "Lunch", "kcal": 750, "fat": 58, "carb": 2, "prot": 52, "ingredients": ["Janjetina", "Mladi luk"], "preparation": "Pečeno meso."},
    {"name": "Punjene paprike (sir/meso)", "type": "Lunch", "kcal": 530, "fat": 39, "carb": 7, "prot": 35, "ingredients": ["Paprike", "Mljeveno meso", "Jaje"], "preparation": "Pecite u pećnici."},

    # --- VEČERA ---
    {"name": "Ribeye Steak", "type": "Dinner", "kcal": 780, "fat": 62, "carb": 0, "prot": 52, "ingredients": ["Steak", "Maslac"], "preparation": "Pecite 3 min sa svake strane."},
    {"name": "Karbonara od tikvica", "type": "Dinner", "kcal": 540, "fat": 42, "carb": 9, "prot": 26, "ingredients": ["Tikvice trake", "Panceta", "Žumanjak"], "preparation": "Pomiješajte vruće tikvice i jaje."},
    {"name": "Mozzarella i rajčica", "type": "Dinner", "kcal": 380, "fat": 30, "carb": 6, "prot": 22, "ingredients": ["Mozzarella", "Rajčica", "Bosiljak"], "preparation": "Caprese salata."},
    {"name": "Svinjski kotlet na masti", "type": "Dinner", "kcal": 610, "fat": 45, "carb": 1, "prot": 42, "ingredients": ["Kotlet", "Svinjska mast"], "preparation": "Ispecite na tavi."},
    {"name": "Salata od hobotnice/plodova", "type": "Dinner", "kcal": 410, "fat": 28, "carb": 4, "prot": 35, "ingredients": ["Plodovi mora", "Maslinovo ulje"], "preparation": "Skuhajte i ohladite."},
    {"name": "Omlet s tartufatom", "type": "Dinner", "kcal": 460, "fat": 38, "carb": 3, "prot": 24, "ingredients": ["3 jaja", "Tartufata"], "preparation": "Ispecite mekani omlet."},
    {"name": "Keto pogačice s čvarcima", "type": "Dinner", "kcal": 520, "fat": 48, "carb": 5, "prot": 18, "ingredients": ["Mljeveni čvarci", "Jaje", "Sir"], "preparation": "Ispecite u kalupima."},
    {"name": "Pečeni Camembert", "type": "Dinner", "kcal": 440, "fat": 36, "carb": 2, "prot": 28, "ingredients": ["Camembert sir", "Orasi"], "preparation": "Pecite u pećnici 15 min."},
    {"name": "Lignje na žaru", "type": "Dinner", "kcal": 480, "fat": 32, "carb": 5, "prot": 40, "ingredients": ["Lignje", "Maslinovo ulje", "Češnjak"], "preparation": "Kratko pecite."},
    {"name": "Carpaccio od govedine", "type": "Dinner", "kcal": 350, "fat": 25, "carb": 1, "prot": 30, "ingredients": ["Sirova govedina", "Parmezan", "Rikula"], "preparation": "Tanko narezano."},
    {"name": "Piletina Parmigiana (Keto)", "type": "Dinner", "kcal": 590, "fat": 42, "carb": 3, "prot": 45, "ingredients": ["Piletina", "Umak od rajčice", "Parmezan"], "preparation": "Zapecite sa sirom."},
    {"name": "Hladna plata (Kulen/Sir)", "type": "Dinner", "kcal": 650, "fat": 55, "carb": 2, "prot": 38, "ingredients": ["Kulen", "Tvrdi sir", "Masline"], "preparation": "Narežite."},
    {"name": "Karfiol s cheddar sirom", "type": "Dinner", "kcal": 410, "fat": 32, "carb": 8, "prot": 18, "ingredients": ["Karfiol", "Cheddar", "Vrhnje"], "preparation": "Zapecite u pećnici."},
    {"name": "Srdele na gradele", "type": "Dinner", "kcal": 390, "fat": 26, "carb": 0, "prot": 36, "ingredients": ["Srdele", "Maslinovo ulje"], "preparation": "Pecite na roštilju/tavi."},
    {"name": "Keto Tacosi (kora od sira)", "type": "Dinner", "kcal": 580, "fat": 45, "carb": 5, "prot": 38, "ingredients": ["Topljeni sir (kora)", "Mljeveno meso"], "preparation": "Otopite sir u krug, napunite mesom."},
    {"name": "Miješano meso", "type": "Dinner", "kcal": 720, "fat": 52, "carb": 1, "prot": 55, "ingredients": ["Ćevapi (bez kruha)", "Vratina"], "preparation": "Roštilj."},
    {"name": "Nicoise salata (Tuna)", "type": "Dinner", "kcal": 490, "fat": 38, "carb": 6, "prot": 30, "ingredients": ["Tuna", "Kuhano jaje", "Mahune"], "preparation": "Složite salatu."},
    {"name": "Kuhane kobasice i senf", "type": "Dinner", "kcal": 620, "fat": 50, "carb": 4, "prot": 32, "ingredients": ["Kobasice", "Senf (bez šećera)"], "preparation": "Skuhajte."},
    {"name": "File oslića na maslacu", "type": "Dinner", "kcal": 430, "fat": 32, "carb": 2, "prot": 35, "ingredients": ["Oslić", "Maslac", "Peršin"], "preparation": "Pecite na tavi."},
    {"name": "Punjeni šampinjoni", "type": "Dinner", "kcal": 380, "fat": 30, "carb": 5, "prot": 20, "ingredients": ["Velike gljive", "Sir", "Slanina"], "preparation": "Napunite klobuke i pecite."},

    # --- SNACK ---
    {"name": "Bademi i orasi", "type": "Snack", "kcal": 190, "fat": 17, "carb": 3, "prot": 6, "ingredients": ["Bademi", "Orasi"], "preparation": "Spremno."},
    {"name": "Masline i kockice sira", "type": "Snack", "kcal": 280, "fat": 26, "carb": 3, "prot": 10, "ingredients": ["Zelene masline", "Gauda"], "preparation": "Narežite."},
    {"name": "Kuhano jaje i majoneza", "type": "Snack", "kcal": 210, "fat": 18, "carb": 1, "prot": 7, "ingredients": ["Jaje", "Majoneza"], "preparation": "Skuhajte."},
    {"name": "Domaći čvarci", "type": "Snack", "kcal": 350, "fat": 32, "carb": 0, "prot": 14, "ingredients": ["Čvarci"], "preparation": "Spremno."},
    {"name": "Pecivo od sira i jaja", "type": "Snack", "kcal": 220, "fat": 18, "carb": 2, "prot": 12, "ingredients": ["Sir", "Jaje"], "preparation": "Ispecite u mikrovalnoj."},
    {"name": "Keto krekeri (lan/sezam)", "type": "Snack", "kcal": 180, "fat": 15, "carb": 4, "prot": 6, "ingredients": ["Sjemenke", "Voda"], "preparation": "Ispecite tanko."},
    {"name": "Lješnjaci (šaka)", "type": "Snack", "kcal": 170, "fat": 16, "carb": 2, "prot": 4, "ingredients": ["Lješnjaci"], "preparation": "Spremno."},
    {"name": "Tamna čokolada 90%", "type": "Snack", "kcal": 120, "fat": 10, "carb": 3, "prot": 2, "ingredients": ["Kockica čokolade"], "preparation": "Spremno."},
    {"name": "Polovica avokada", "type": "Snack", "kcal": 240, "fat": 22, "carb": 3, "prot": 2, "ingredients": ["Avokado", "Sol"], "preparation": "Posolite."},
    {"name": "Beef Jerky (suho meso)", "type": "Snack", "kcal": 150, "fat": 6, "carb": 2, "prot": 22, "ingredients": ["Sušena govedina"], "preparation": "Spremno."},
    {"name": "Krastavci s vrhnjem", "type": "Snack", "kcal": 140, "fat": 12, "carb": 4, "prot": 3, "ingredients": ["Krastavac", "Kiselo vrhnje"], "preparation": "Narežite."},
    {"name": "Tostirani bademi", "type": "Snack", "kcal": 180, "fat": 17, "carb": 3, "prot": 4, "ingredients": ["Bademi"], "preparation": "Kratko popržite."},
    {"name": "Čips od parmezana", "type": "Snack", "kcal": 190, "fat": 14, "carb": 1, "prot": 15, "ingredients": ["Parmezan"], "preparation": "Otopite hrpice sira dok ne budu hrskave."},
    {"name": "Rolice šunke i sira", "type": "Snack", "kcal": 210, "fat": 16, "carb": 2, "prot": 14, "ingredients": ["Šunka", "Sir listići"], "preparation": "Zarolajte."},
    {"name": "Chia sjemenke u jogurtu", "type": "Snack", "kcal": 220, "fat": 18, "carb": 5, "prot": 8, "ingredients": ["Chia", "Jogurt"], "preparation": "Pustite da nabubri."},
    {"name": "Maslac od badema (žlica)", "type": "Snack", "kcal": 100, "fat": 9, "carb": 2, "prot": 4, "ingredients": ["Bademov maslac"], "preparation": "Spremno."},
    {"name": "Listići kokosa", "type": "Snack", "kcal": 150, "fat": 14, "carb": 3, "prot": 1, "ingredients": ["Kokos čips"], "preparation": "Spremno."},
    {"name": "Suncokretove sjemenke", "type": "Snack", "kcal": 160, "fat": 14, "carb": 4, "prot": 6, "ingredients": ["Suncokret"], "preparation": "Spremno."},
    {"name": "Brazilski orah (2 kom)", "type": "Snack", "kcal": 70, "fat": 7, "carb": 1, "prot": 1, "ingredients": ["Brazilski orah"], "preparation": "Spremno."},
    {"name": "Kuglice od krem sira", "type": "Snack", "kcal": 230, "fat": 20, "carb": 2, "prot": 10, "ingredients": ["Krem sir", "Sezam"], "preparation": "Uvaljajte sir u sezam."},
]

# --- 3. LOGIKA IZRAČUNA MAKROSA ---
def calculate_macros(spol, tezina, visina, godine, aktivnost, cilj):
    # Mifflin-St Jeor formula
    if spol == "Muško":
        bmr = 10 * tezina + 6.25 * visina - 5 * godine + 5
    else:
        bmr = 10 * tezina + 6.25 * visina - 5 * godine - 161
    
    act_mult = {
        "Sjedilački": 1.2, 
        "Lagano": 1.375, 
        "Umjereno": 1.55, 
        "Vrlo aktivno": 1.725
    }
    
    tdee = bmr * act_mult[aktivnost]
    
    if cilj == "Gubitak masti": target_kcal = tdee * 0.8
    elif cilj == "Dobivanje mišića": target_kcal = tdee * 1.1
    else: target_kcal = tdee # Održavanje
    
    # Keto omjeri: 70% Masti, 25% Proteini, 5% UH
    return {
        "kcal": int(target_kcal),
        "fat": int((target_kcal * 0.7) / 9),
        "prot": int((target_kcal * 0.25) / 4),
        "carb": int((target_kcal * 0.05) / 4)
    }

# --- 4. GLAVNO SUČELJE (TABS) ---
t_prof, t_fast, t_menu, t_prog = st.tabs(["👤 Profil", "🕒 Post", "🥗 Personalizirani Menu", "📈 Napredak"])

# ---------------- TAB 1: PROFIL ----------------
with t_prof:
    st.header("Postavke Profila")
    p_df = load_data(PROFILE_FILE, ["Ime", "Spol", "Tezina", "Visina", "Godine", "Aktivnost", "Cilj"])
    init = p_df.iloc[0] if not p_df.empty else None
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            ime = st.text_input("Ime", value=init["Ime"] if init is not None else "")
            spol = st.selectbox("Spol", ["Muško", "Žensko"], index=0 if init is None or init["Spol"]=="Muško" else 1)
            godine = st.number_input("Godine", min_value=10, max_value=100, value=int(init["Godine"]) if init is not None else 30)
        with col2:
            tezina = st.number_input("Težina (kg)", min_value=30.0, max_value=200.0, value=float(init["Tezina"]) if init is not None else 80.0)
            visina = st.number_input("Visina (cm)", min_value=100.0, max_value=250.0, value=float(init["Visina"]) if init is not None else 180.0)
            cilj = st.selectbox("Cilj", ["Gubitak masti", "Održavanje", "Dobivanje mišića"], index=0 if init is None else ["Gubitak masti", "Održavanje", "Dobivanje mišića"].index(init["Cilj"]))
        
        aktivnost = st.select_slider("Razina aktivnosti", options=["Sjedilački", "Lagano", "Umjereno", "Vrlo aktivno"], value=init["Aktivnost"] if init is not None else "Sjedilački")
        
        submit = st.form_submit_button("Spremi Profil")
        
        if submit:
            # Spremanje profila
            new_profile = pd.DataFrame([{"Ime": ime, "Spol": spol, "Tezina": tezina, "Visina": visina, "Godine": godine, "Aktivnost": aktivnost, "Cilj": cilj}])
            save_data(new_profile, PROFILE_FILE)
            
            # Automatsko spremanje kilaže u povijest (za grafikon)
            w_df = load_data(WEIGHT_FILE, ["Datum", "Tezina"])
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            # Dodaj novi zapis
            new_weight = pd.DataFrame([{"Datum": current_date, "Tezina": tezina}])
            # Spoji i makni duplikate za isti dan (zadrži zadnji unos)
            w_df = pd.concat([w_df, new_weight]).drop_duplicates(subset="Datum", keep="last")
            save_data(w_df, WEIGHT_FILE)
            
            st.success("Profil spremljen! Kilaža zabilježena u grafikonu.")
            st.rerun()

# ---------------- TAB 2: POST (DETALJNE METODE + DVIJE ŠTOPERICE) ----------------
with t_fast:
    st.header("🕒 Fasting Tajmer & Plan")

    # Proširena definicija planova s tvojim uputama
    fasting_plans = {
        "16:8": {
            "sati": 16, 
            "info": "16 sati posta, 8 sati za jelo (Npr. jedeš od 12:00 do 20:00).",
            "preporuka": "👉 Najpopularniji i najlakši za početnike."
        },
        "14:10": {
            "sati": 14, 
            "info": "14 sati posta, 10 sati za jelo. Blaža verzija 16:8.",
            "preporuka": "👉 Dobar ako tek ulaziš u IF (Intermittent Fasting)."
        },
        "18:6": {
            "sati": 18, 
            "info": "18 sati posta, 6 sati za jelo.",
            "preporuka": "👉 Malo zahtjevniji, ali efikasniji za gubitak masti."
        },
        "20:4 (Warrior diet)": {
            "sati": 20, 
            "info": "20 sati posta, 4 sata za jelo. Često jedan veći obrok dnevno.",
            "preporuka": "👉 Nije za svakoga, traži disciplinu."
        },
        "OMAD (One Meal A Day)": {
            "sati": 23, 
            "info": "Jedan obrok dnevno. 23 sata posta.",
            "preporuka": "👉 Ekstremnija varijanta, oprezno s nutritivnim balansom."
        },
        "5:2 metoda": {
            "sati": 24, 
            "info": "5 dana jedeš normalno, 2 dana znatno smanjiš kalorije (≈500–600 kcal).",
            "preporuka": "👉 Fleksibilno, bez svakodnevnog posta."
        },
        "Alternating Day Fasting": {
            "sati": 36, 
            "info": "Jedan dan jedeš normalno, drugi dan postiš ili jedeš minimalno.",
            "preporuka": "👉 Teško za dugoročno održavanje."
        }
    }

    # Inicijalizacija stanja
    if "is_fasting" not in st.session_state:
        st.session_state.is_fasting = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None

    f_df = load_data(FAST_FILE, ["Metoda", "Početak", "Kraj", "Trajanje_h", "Cilj_h"])

    # 1. ODABIR PLANA I PRIKAZ DETALJNIH UPUTA
    if not st.session_state.is_fasting:
        selected_plan_name = st.selectbox("Odaberi metodu posta:", list(fasting_plans.keys()))
        
        # Prikaz opširnog info boxa prema tvojim uputama
        with st.expander("ℹ️ Detalji odabrane metode", expanded=True):
            st.write(f"**Opis:** {fasting_plans[selected_plan_name]['info']}")
            st.write(f"**Savjet:** {fasting_plans[selected_plan_name]['preporuka']}")
        
        st.session_state.current_goal = fasting_plans[selected_plan_name]["sati"]
        st.session_state.plan_name = selected_plan_name
    else:
        st.subheader(f"Trenutna metoda: {st.session_state.plan_name}")
        st.info(f"{fasting_plans[st.session_state.plan_name]['info']}")

    st.divider()

    # 2. LOGIKA ŠTOPERICA (Kao u prošlom koraku)
    col_gumbi, col_timer1, col_timer2 = st.columns([1, 1, 1])

    if st.session_state.is_fasting:
        now = datetime.datetime.now()
        diff = now - st.session_state.start_time
        total_seconds = int(diff.total_seconds())
        
        # Štoperica 1: Proteklo
        s_p, m_p, sec_p = total_seconds // 3600, (total_seconds % 3600) // 60, total_seconds % 60
        # Štoperica 2: Preostalo
        target_sec = st.session_state.current_goal * 3600
        rem_sec = max(target_sec - total_seconds, 0)
        s_o, m_o, sec_o = rem_sec // 3600, (rem_sec % 3600) // 60, rem_sec % 60

        with col_timer1:
            st.metric("Vrijeme posta", f"{s_p:02d}:{m_p:02d}:{sec_p:02d}")
        with col_timer2:
            st.metric("Ostalo do cilja", f"{s_o:02d}:{m_o:02d}:{sec_o:02d}", 
                      delta="GOTOVO" if rem_sec == 0 else None)

        st.progress(min(total_seconds / target_sec, 1.0))

        with col_gumbi:
            if st.button("🍽️ ZAVRŠI POST", use_container_width=True, type="primary"):
                end_time = datetime.datetime.now()
                duration_h = round((end_time - st.session_state.start_time).total_seconds() / 3600, 2)
                
                new_fast = pd.DataFrame([{
                    "Metoda": st.session_state.plan_name,
                    "Početak": st.session_state.start_time.strftime("%d.%m. %H:%M"),
                    "Kraj": end_time.strftime("%d.%m. %H:%M"),
                    "Trajanje_h": duration_h,
                    "Cilj_h": st.session_state.current_goal
                }])
                f_df = pd.concat([f_df, new_fast], ignore_index=True)
                save_data(f_df, FAST_FILE)
                st.session_state.is_fasting = False
                st.rerun()

        import time
        time.sleep(1)
        st.rerun()

    else:
        with col_gumbi:
            if st.button("🚀 KRENI S POSTOM", use_container_width=True, type="primary"):
                st.session_state.start_time = datetime.datetime.now()
                st.session_state.is_fasting = True
                st.rerun()

    # 3. POVIJEST
    if not f_df.empty:
        st.divider()
        st.subheader("📋 Povijest postova")
        st.dataframe(f_df.iloc[::-1], use_container_width=True, hide_index=True)

# ---------------- TAB 3: GENERATOR JELOVNIKA ----------------
with t_menu:
    st.header("🥗 Keto Menu Generator")
    
    # Parametri za generiranje
    col_kat1, col_kat2 = st.columns(2)
    with col_kat1:
        cilj = st.selectbox("Cilj:", ["Gubitak masnoće", "Održavanje", "Dobivanje mišića"])
    with col_kat2:
        broj_obroka = st.slider("Broj obroka dnevno:", 1, 4, 2)

    if st.button("✨ Generiraj personalizirani meni", use_container_width=True):
        with st.spinner("Računam nutritivne vrijednosti..."):
            # OVDJE IDE TVOJA FUNKCIJA ZA POZIV AI-a (npr. get_keto_menu)
            # Pretpostavimo da AI vraća rječnik 'generated_menu'
            # Primjer strukture koju AI treba vratiti:
            # {
            #   "Meni 1 (750 kcal | P: 50g, U: 10g, M: 60g)": [
            #       {"n": "Piletina", "g": "200g", "m": "P:46g, U:0g, M:6g"},
            #       {"n": "Avokado", "g": "100g", "m": "P:2g, U:2g, M:15g"}
            #   ],
            #   "Meni 2 (...": [...]
            # }
            st.session_state.last_menu = generated_menu # Spremamo u session state

    # PRIKAZ MENIJA
    if "last_menu" in st.session_state:
        st.write("### Prijedlozi obroka:")
        
        for menu_naslov, namirnice in st.session_state.last_menu.items():
            # st.expander je po defaultu ZATVOREN (expanded=False)
            with st.expander(f"🍴 {menu_naslov}", expanded=False):
                # Zaglavlje unutar expandera
                cols = st.columns([3, 2, 3])
                cols[0].write("**Namirnica**")
                cols[1].write("**Količina**")
                cols[2].write("**Makrosi**")
                st.divider()

                for stavka in namirnice:
                    c1, c2, c3 = st.columns([3, 2, 3])
                    c1.write(stavka['n']) # Naziv namirnice
                    c2.write(f"`{stavka['g']}`") # Gramaža (označeno kao kod za vidljivost)
                    c3.write(f"*{stavka['m']}*") # Makrosi namirnice (italic)
                
                st.button(f"Spremi ovaj meni u povijest", key=menu_naslov)

# ---------------- TAB 4: NAPREDAK ----------------
with t_prog:
    st.header("📈 Tvoj Napredak")
    
    # 1. GRAFIKON KILAŽE
    st.subheader("1. Promjena tjelesne težine")
    
    # Učitavanje s provjerom stupaca
    w_df = load_data(WEIGHT_FILE, ["Datum", "Tezina"])
    
    if not w_df.empty and len(w_df) > 0:
        # Sortiraj po datumu
        w_df = w_df.sort_values("Datum")
        fig_weight = px.line(w_df, x="Datum", y="Tezina", markers=True, title="Kilaža kroz vrijeme (kg)")
        fig_weight.update_traces(line_color="#2ECC71", line_width=3)
        st.plotly_chart(fig_weight, use_container_width=True)
    else:
        st.info("Grafikon težine će se prikazati nakon što spremite profil barem jednom.")

    st.divider()

    # 2. GRAFIKON POSTA
    st.subheader("2. Povijest posta")
    f_df = load_data(FAST_FILE, ["Datum", "Sati"])
    
    if not f_df.empty and len(f_df) > 0:
        f_df = f_df.sort_values("Datum")
        fig_fast = px.bar(f_df, x="Datum", y="Sati", title="Trajanje posta po danima (h)")
        fig_fast.update_traces(marker_color="#3498DB")
        # Dodaj liniju cilja (npr. 16h)
        fig_fast.add_hline(y=16, line_dash="dot", annotation_text="Cilj (16h)", annotation_position="bottom right")
        st.plotly_chart(fig_fast, use_container_width=True)
    else:
        st.info("Grafikon posta će se prikazati nakon što zabilježite prvi post u tabu 'Post'.")
