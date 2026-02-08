import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. KONFIGURACIJA I PODACI ---
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

# --- 2. PROŠIRENE KNJIŽNICE (LIBRARIES) ---

KETO_FOODS = {
    "Avocado": {"Fat": 15, "NetCarb": 2, "Protein": 2, "Unit": "100g"},
    "Chicken Thigh": {"Fat": 15, "NetCarb": 0, "Protein": 20, "Unit": "100g"},
    "Spinach": {"Fat": 0, "NetCarb": 1, "Protein": 3, "Unit": "100g"},
    "Ribeye Steak": {"Fat": 22, "NetCarb": 0, "Protein": 24, "Unit": "100g"},
    "Salmon (Fatty)": {"Fat": 13, "NetCarb": 0, "Protein": 20, "Unit": "100g"},
    "Eggs": {"Fat": 5, "NetCarb": 0.6, "Protein": 6, "Unit": "1 Large"},
    "Butter": {"Fat": 12, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
    "MCT Oil": {"Fat": 14, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
    "Bacon": {"Fat": 42, "NetCarb": 1.4, "Protein": 37, "Unit": "100g"},
    "Pecans": {"Fat": 72, "NetCarb": 4, "Protein": 9, "Unit": "100g"},
    "Zucchini": {"Fat": 0.3, "NetCarb": 2.1, "Protein": 1.2, "Unit": "100g"},
    "Heavy Cream": {"Fat": 5, "NetCarb": 0.4, "Protein": 0.4, "Unit": "1 tbsp"},
    "Parmesan Cheese": {"Fat": 28, "NetCarb": 4, "Protein": 38, "Unit": "100g"},
    "Broccoli": {"Fat": 0.4, "NetCarb": 4, "Protein": 2.8, "Unit": "100g"},
    "Olive Oil": {"Fat": 14, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
    "Walnuts": {"Fat": 65, "NetCarb": 7, "Protein": 15, "Unit": "100g"}
}

SUPPLEMENT_DB = {
    "Magnesium Glycinate": {"dose": "400mg", "timing": "30 min prije spavanja", "logic": "Sprečava grčeve u mišićima i poboljšava san."},
    "Potassium Chloride": {"dose": "1000mg", "timing": "Uz obrok", "logic": "Ključan za energiju i sprečavanje 'Keto gripe'."},
    "Sodium (Sea Salt)": {"dose": "2-3g extra", "timing": "Tijekom posta", "logic": "Sprečava glavobolje uzrokovane gubitkom elektrolita."},
    "Omega-3 (Fish Oil)": {"dose": "2000mg", "timing": "Uz najmasniji obrok", "logic": "Smanjuje upalne procese."},
    "Vitamin D3 + K2": {"dose": "5000 IU", "timing": "Ujutro uz masnoću", "logic": "Hormonalno zdravlje i apsorpcija kalcija."},
    "Apple Cider Vinegar": {"dose": "1 žlica u vodi", "timing": "Prije obroka", "logic": "Poboljšava osjetljivost na inzulin i probavu."},
    "Creatine Monohydrate": {"dose": "5g", "timing": "Bilo kada", "logic": "Pomaže u očuvanju mišićne mase tijekom ketoze."}
}

RECIPES_DB = [
    {
        "name": "Crispy Salmon & Asparagus",
        "fridge": ["Salmon (Fatty)", "Butter"],
        "buy": ["Asparagus", "Lemon", "Garlic"],
        "instructions": "Peci losos na maslacu 4 min s kožom prema dolje na 200°C. Dodaj šparoge u istu tavu.",
        "links": ["https://www.dietdoctor.com/recipes/baked-salmon-with-asparagus", "https://www.youtube.com/results?search_query=keto+salmon+asparagus"]
    },
    {
        "name": "Keto Ribeye Feast",
        "fridge": ["Ribeye Steak", "Butter"],
        "buy": ["Fresh Rosemary", "Broccoli", "Garlic"],
        "instructions": "Naglo peci na 220°C. Prelivaj maslacem, ružmarinom i češnjakom. Posluži uz brokulu.",
        "links": ["https://www.delish.com/cooking/recipe/steak-keto", "https://www.youtube.com/results?search_query=perfect+keto+ribeye"]
    },
    {
        "name": "Bacon & Egg Avocado Bowls",
        "fridge": ["Eggs", "Bacon", "Avocado"],
        "buy": ["Chives", "Black Pepper"],
        "instructions": "Prereži avokado, izvadi košticu, razbij jaje u rupu. Peci na 200°C 15 min. Pospi slaninom.",
        "links": ["https://www.allrecipes.com/recipe/244257/baked-eggs-in-avocado/", "https://www.youtube.com/results?search_query=keto+avocado+egg+boats"]
    }
]

# --- 3. INTERFEJS APLIKACIJE ---

st.title("🥑 Keto Intelligence Pro")

tab1, tab2, tab3, tab4 = st.tabs(["🕒 Post (Fasting)", "🥗 Hrana i Recepti", "💊 Suplementi", "📈 Napredak"])

# --- TAB 1: POST ---
with tab1:
    st.header("16/8 Fasting Tracker")
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Pokreni Post"):
            st.session_state.start_time = datetime.datetime.now()
    with c2:
        if st.button("🍽️ Završi i Zapremi"):
            if st.session_state.start_time:
                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
                new_fast = pd.DataFrame({"Datum": [datetime.date.today().strftime('%Y-%m-%d')], "Sati": [round(duration, 2)]})
                save_data(pd.concat([load_data(FAST_FILE, ["Datum", "Sati"]), new_fast]), FAST_FILE)
                st.session_state.start_time = None
                st.success(f"Zapisano: {duration:.1f} sati posta!")

    if st.session_state.start_time:
        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600
        st.metric("Trenutno vrijeme posta", f"{elapsed:.1f} h")
        st.progress(min(elapsed/16, 1.0))
    
    st.subheader("📜 Povijest posta")
    history_df = load_data(FAST_FILE, ["Datum", "Sati"])
    if not history_df.empty:
        st.line_chart(history_df.set_index("Datum"))
        st.dataframe(history_df.tail(5), use_container_width=True)

# --- TAB 2: HRANA I RECEPTI ---
with tab2:
    st.header("Keto Knjižnica Hrane")
    search_food = st.multiselect("Odaberi namirnice koje imaš u hladnjaku:", list(KETO_FOODS.keys()))
    
    shopping_list = []

    if search_food:
        st.write("### 📊 Makronutrijenti")
        for f in search_food:
            m = KETO_FOODS[f]
            st.caption(f"**{f}**: {m['Fat']}g Masti | {m['NetCarb']}g Ugljikohidrata | {m['Protein']}g Proteina")
        
        st.divider()
        st.header("🍳 Preporučeni Recepti")
        for r in RECIPES_DB:
            if any(item in search_food for item in r['fridge']):
                with st.expander(f"⭐ {r['name']}"):
                    st.write(f"**📝 Koraci:** {r['instructions']}")
                    st.write(f"**🛒 Potrebno kupiti:** {', '.join(r['buy'])}")
                    shopping_list.extend(r['buy'])
                    for link in r['links']:
                        st.write(f"- [Video/Vodič]({link})")
        
        if shopping_list:
            st.divider()
            st.subheader("🛒 Automatska lista za kupovinu")
            unique_items = list(set(shopping_list))
            for item in unique_items:
                st.write(f"- [ ] {item}")

# --- TAB 3: SUPLEMENTI ---
with tab3:
    st.header("Protokol Suplemenata")
    my_stack = st.multiselect("Dodaj suplemente koje koristiš:", list(SUPPLEMENT_DB.keys()))
    
    for s in my_stack:
        data = SUPPLEMENT_DB[s]
        with st.expander(f"💊 {s}"):
            st.write(f"**Doza:** {data['dose']}")
            st.write(f"**Kada uzimati:** {data['timing']}")
            st.info(f"**Zašto:** {data['logic']}")

# --- TAB 4: NAPREDAK ---
with tab4:
    st.header("Praćenje Težine (kg)")
    w_val = st.number_input("Unesi trenutnu težinu (kg)", min_value=30.0, step=0.1)
    if st.button("Spremi Težinu"):
        new_w = pd.DataFrame({"Datum": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [w_val]})
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Datum", "Weight_kg"]), new_w]), WEIGHT_FILE)
    
    df_w = load_data(WEIGHT_FILE, ["Datum", "Weight_kg"])
    if not df_w.empty:
        df_w['Datum'] = pd.to_datetime(df_w['Datum'])
        st.line_chart(df_w.set_index("Datum"))

    st.divider()
    st.header("🧮 Brzi Macro Kalkulator")
    c1, c2 = st.columns(2)
    with c1:
        target_calories = st.number_input("Ciljane kalorije (kcal)", value=2000, step=50)
    with c2:
        protein_ratio = st.slider("Protein % (Keto standard je 20-25%)", 15, 35, 25)
    
    # Izračun (9 kcal/g masti, 4 kcal/g proteina/UH)
    prot_g = (target_calories * (protein_ratio/100)) / 4
    carb_g = (target_calories * 0.05) / 4 # 5% UH standard
    fat_g = (target_calories * (1 - (protein_ratio/100) - 0.05)) / 9

    st.success(f"Dnevni ciljevi: **{round(fat_g)}g Masti** | **{round(prot_g)}g Proteina** | **{round(carb_g)}g Ugljikohidrata**")
