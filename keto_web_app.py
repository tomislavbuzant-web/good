import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. KONFIGURACIJA I STILIZACIJA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# CSS ostaje isti, osiguravamo da nema grešaka u renderiranju
st.markdown("""
    <style>
    .main { background-color: #f1f3f5; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #2e7d32; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 8px 8px 0 0; 
        padding: 10px 15px;
        border: 1px solid #ddd;
    }
    .stButton>button { border-radius: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Datoteke za pohranu
FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns, initial_val=None):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame(columns=columns)
    if initial_val:
        return pd.DataFrame(initial_val)
    return pd.DataFrame(columns=columns)

def format_euro_date(date_str):
    try:
        return pd.to_datetime(date_str).strftime('%d.%m.%Y')
    except:
        return date_str

# --- 2. KETO BAZA PODATAKA (USDA-BASED) ---
# Popravljeno: Svi navodnici su zatvoreni i nema grešaka u sintaksi
USDA_KETO = {
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290},
    "Jaja (L veličina)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70},
    "Maslac (15g)": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100},
    "Losos (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200},
    "Avokado (Srednji)": {"fat": 21, "prot": 3, "carb": 3, "cal": 240},
    "Pileći zabatak (100g)": {"fat": 15, "prot": 20, "carb": 0, "cal": 210},
    "Kokosovo ulje (1 žlica)": {"fat": 14, "prot": 0, "carb": 0, "cal": 120},
    "Slanina (2 šnite)": {"fat": 7, "prot": 6, "carb": 0, "cal": 90},
    "Špinat (100g)": {"fat": 0.4, "prot": 2.9, "carb": 1.4, "cal": 23},
    "Pekan orasi (30g)": {"fat": 20, "prot": 3, "carb": 1.2, "cal": 200}
}

# --- 3. SIDEBAR (PROFIL) ---
st.sidebar.title("🥑 Keto Pro Profil")
profile_pic = st.sidebar.file_uploader("Učitaj fotografiju", type=['jpg', 'png'])
if profile
