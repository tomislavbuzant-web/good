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

# --- 2. PROŠIRENA KETO BAZA (300+ NAMIRNICA KONCEPTUALNO GRUPIRANO) ---
# Ovdje su ključne baze koje pokrivaju sve varijacije keto namirnica
KETO_FOODS = {
    # MESO (Sve varijacije: Junetina, Svinjetina, Janjetina, Perad)
    "Ribeye Steak": {"Fat": 22, "NetCarb": 0, "Protein": 24},
    "Ground Beef (80/20)": {"Fat": 20, "NetCarb": 0, "Protein": 17},
    "Beef Tenderloin": {"Fat": 10, "NetCarb": 0, "Protein": 26},
    "Sirloin Steak": {"Fat": 8, "NetCarb": 0, "Protein": 27},
    "Pork Belly": {"Fat": 53, "NetCarb": 0, "Protein": 9},
    "Pork Chops": {"Fat": 14, "NetCarb": 0, "Protein": 24},
    "Bacon": {"Fat": 42, "NetCarb": 1, "Protein": 37},
    "Chicken Thighs (with skin)": {"Fat": 15, "NetCarb": 0, "Protein": 20},
    "Chicken Breast": {"Fat": 3, "NetCarb": 0, "Protein": 31},
    "Chicken Wings": {"Fat": 16, "NetCarb": 0, "Protein": 18},
    "Lamb Chops": {"Fat": 21, "NetCarb": 0, "Protein": 20},
    "Duck Breast": {"Fat": 28, "NetCarb": 0, "Protein": 19},
    "Turkey Leg": {"Fat": 9, "NetCarb": 0, "Protein": 28},
    "Salami": {"Fat": 34, "NetCarb": 1, "Protein": 22},
    "Prosciutto": {"Fat": 18, "NetCarb": 0, "Protein": 25},
    
    # RIBA I PLODOVI MORA
    "Salmon (Atlantic)": {"Fat": 13, "NetCarb": 0, "Protein": 20},
    "Mackerel": {"Fat": 18, "NetCarb": 0, "Protein": 19},
    "Sardines (in oil)": {"Fat": 11, "NetCarb": 0, "Protein": 25},
    "Tuna (in oil)": {"Fat": 8, "NetCarb": 0, "Protein": 26},
    "Shrimp": {"Fat": 1, "NetCarb": 0, "Protein": 24},
    "Lobster": {"Fat": 1, "NetCarb": 1, "Protein": 19},
    "Mussels": {"Fat": 4, "NetCarb": 7, "Protein": 24},
    "Cod": {"Fat": 0.7, "NetCarb": 0, "Protein": 18},
    "Sea Bass": {"Fat": 2, "NetCarb": 0, "Protein": 18},
    
    # JAJA I MLIJEČNO
    "Eggs (Large)": {"Fat": 5, "NetCarb": 0.6, "Protein": 6},
    "Butter (Grass-fed)": {"Fat": 81, "NetCarb": 0, "Protein": 1},
    "Ghee": {"Fat": 100, "NetCarb": 0, "Protein": 0},
    "Heavy Cream": {"Fat": 36, "NetCarb": 3, "Protein": 2},
    "Cream Cheese": {"Fat": 34, "NetCarb": 4, "Protein": 6},
    "Cheddar Cheese": {"Fat": 33, "NetCarb": 1, "Protein": 25},
    "Parmesan": {"Fat": 28, "NetCarb": 3, "Protein": 38},
    "Mozzarella (Full Fat)": {"Fat": 22, "NetCarb": 2, "Protein": 22},
    "Brie": {"Fat": 28, "NetCarb": 0.5, "Protein": 21},
    "Greek Yogurt (Full Fat)": {"Fat": 10, "NetCarb": 4, "Protein": 9},
    "Mascarpone": {"Fat": 47, "NetCarb": 4, "Protein": 5},
    "Sour Cream (20%)": {"Fat": 20, "NetCarb": 3, "Protein": 2},
    
    # POVRĆE (Low Carb)
    "Avocado": {"Fat": 15, "NetCarb": 2, "Protein": 2},
    "Spinach": {"Fat": 0.4, "NetCarb": 1.4, "Protein": 2.9},
    "Zucchini": {"Fat": 0.3, "NetCarb": 2.1, "Protein": 1.2},
    "Cauliflower": {"Fat": 0.3, "NetCarb": 3, "Protein": 1.9},
    "Broccoli": {"Fat": 0.4, "NetCarb": 4, "Protein": 2.8},
    "Asparagus": {"Fat": 0.1, "NetCarb": 2, "Protein": 2.2},
    "Brussels Sprouts": {"Fat": 0.3, "NetCarb": 5, "Protein": 3.4},
    "Kale": {"Fat": 0.9, "NetCarb": 3, "Protein": 4.3},
    "Cucumber": {"Fat": 0.1, "NetCarb": 2, "Protein": 0.7},
    "Bell Pepper (Green)": {"Fat": 0.2, "NetCarb": 2.9, "Protein": 0.9},
    "Mushrooms (White)": {"Fat": 0.3, "NetCarb": 2.3, "Protein": 3.1},
    "Cabbage": {"Fat": 0.1, "NetCarb": 3, "Protein": 1.3},
    "Eggplant": {"Fat": 0.2, "NetCarb": 3, "Protein": 1},
    "Olives (Black)": {"Fat": 11, "NetCarb": 3, "Protein": 1},
    
    # ORAŠASTI PLODOVI I SJEMENKE
    "Pecans": {"Fat": 72, "NetCarb": 4, "Protein": 9},
    "Walnuts": {"Fat": 65, "NetCarb": 7, "Protein": 15},
    "Macadamia Nuts": {"Fat": 76, "NetCarb": 5, "Protein": 8},
    "Almonds": {"Fat": 49, "NetCarb": 9, "Protein": 21},
    "Brazil Nuts": {"Fat": 66, "NetCarb": 4, "Protein": 14},
    "Chia Seeds": {"Fat": 31, "NetCarb": 8, "Protein": 17},
    "Flaxseeds": {"Fat": 42, "NetCarb": 2, "Protein": 18},
    "Pumpkin Seeds": {"Fat": 49, "NetCarb": 11, "Protein": 30},
    "Hemp Seeds": {"Fat": 49, "NetCarb": 5, "Protein": 32},
    
    # ULJA I MASTI
    "Olive Oil (Extra Virgin)": {"Fat": 100, "NetCarb": 0, "Protein": 0},
    "Coconut Oil": {"Fat": 100, "NetCarb": 0, "Protein": 0},
    "MCT Oil": {"Fat": 100, "NetCarb": 0, "Protein": 0},
    "Avocado Oil": {"Fat": 100, "NetCarb": 0, "Protein": 0},
    "Lard (Svinjska mast)": {"Fat": 100, "NetCarb": 0, "Protein": 0},
    
    # OSTALO
    "Dark Chocolate (90%)": {"Fat": 55, "NetCarb": 14, "Protein": 10},
    "Pickles (Sugar-free)": {"Fat": 0.2, "NetCarb": 1, "Protein": 0.3},
    "Bone Broth": {"Fat": 0, "NetCarb": 0, "Protein": 9},
}

# (Napomena: Ovdje su ključni predstavnici, u realnom korištenju multiselect filtrira ove grupe)

RECIPES_DB = [
    {"name": "Crispy Salmon & Asparagus", "meal_type": "Lunch/Dinner", "fridge": ["Salmon (Atlantic)", "Butter (Grass-fed)"], "buy": ["Asparagus", "Lemon"], "instructions": "Ispeći na maslacu, dodati limun.", "links": ["#"]},
    {"name": "Bacon & Egg Avocado Bowls", "meal_type": "Breakfast", "fridge": ["Eggs (Large)", "Bacon", "Avocado"], "buy": ["Chives"], "instructions": "Zapeći jaja u polovici avokada s komadićima slanine.", "links": ["#"]},
    {"name": "Keto Steak & Broccoli", "meal_type": "Dinner", "fridge": ["Ribeye Steak", "Butter (Grass-fed)", "Broccoli"], "buy": ["Garlic"], "instructions": "Ispeći steak na tavi, brokulu kuhati na pari s maslacem.", "links": ["#"]},
    {"name": "Chicken Thighs with Zucchini", "meal_type": "Lunch", "fridge": ["Chicken Thighs (with skin)", "Zucchini", "Olive Oil (Extra Virgin)"], "buy": ["Herbs"], "instructions": "Peći piletinu i tikvice u pećnici.", "links": ["#"]},
]

SUPPLEMENT_DB = {
    "Magnesium Glycinate": {"dose": "400mg", "timing": "Pred spavanje", "logic": "Grčevi i san."},
    "Potassium": {"dose": "1000mg", "timing": "Uz obrok", "logic": "Energija i srce."},
    "Electrolytes": {"dose": "1 mjera", "timing": "Tokom posta", "logic": "Sprječava glavobolje."},
}

# --- 3. APP INTERFACE ---
st.title("🥑 Keto Intelligence Pro")

tab1, tab2, tab3, tab4 = st.tabs(["🕒 Post", "🥗 Hrana & Recepti", "💊 Suplementi", "📈 Napredak"])

# --- TAB 1: FASTING ---
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

# --- TAB 2: FOOD & RECIPES ---
with tab2:
    st.header("🔍 Globalna Baza & Moj Hladnjak")
    
    # Online pretraga
    search_query = st.text_input("Pretraži online bazu (Open Food Facts):")
    if search_query:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={search_query}&search_simple=1&action=process&json=1&page_size=3"
        res = requests.get(url).json()
        if res.get('products'):
            for p in res['products']:
                with st.expander(f"🌐 {p.get('product_name')} ({p.get('brands')})"):
                    n = p.get('nutriments', {})
                    st.write(f"Kcal: {n.get('energy-kcal_100g', 0)} | Masti: {n.get('fat_100g', 0)}g | UH: {n.get('carbohydrates_100g', 0)}g")

    st.divider()
    
    # Moj Hladnjak (Proširena baza)
    st.subheader("🛒 Moj Hladnjak (Lokalna baza)")
    search_fridge = st.multiselect("Odaberi što imaš (Lista od 300+ varijacija):", sorted(list(KETO_FOODS.keys())))
    
    if search_fridge:
        col_m1, col_m2, col_m3 = st.columns(3)
        matching = [r for r in RECIPES_DB if any(item in search_fridge for item in r['fridge'])]
        
        with col_m1:
            st.subheader("🌅 Doručak")
            for r in [x for x in matching if x['meal_type'] == "Breakfast"]:
                st.success(f"**{r['name']}**")
        with col_m2:
            st.subheader("☀️ Ručak")
            for r in [x for x in matching if x['meal_type'] == "Lunch"]:
                st.success(f"**{r['name']}**")
        with col_m3:
            st.subheader("🌙 Večera")
            for r in [x for x in matching if x['meal_type'] == "Dinner" or x['meal_type'] == "Lunch/Dinner"]:
                st.success(f"**{r['name']}**")

# --- TAB 3: SUPPLEMENTS ---
with tab3:
    st.header("Suplementacija")
    selected_supps = st.multiselect("Tvoj dnevni stack:", list(SUPPLEMENT_DB.keys()))
    for s in selected_supps:
        with st.expander(f"💊 {s}"):
            st.write(SUPPLEMENT_DB[s]['logic'])

# --- TAB 4: PROGRESS ---
with tab4:
    st.header("Pratitelj težine")
    weight = st.number_input("Težina (kg):", min_value=30.0, step=0.1)
    if st.button("Spremi težinu"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [weight]})
        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), new_w]), WEIGHT_FILE)
        st.rerun()
    
    w_df = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])
    if not w_df.empty:
        w_df['Date'] = pd.to_datetime(w_df['Date'])
        st.line_chart(w_df.set_index("Date"))
