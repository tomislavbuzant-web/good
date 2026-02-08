import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. KONFIGURACIJA I MINIMALISTIČKI DIZAJN ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

st.markdown("""
    <style>
    /* Glavna pozadina i fontovi */
    .main { background-color: #fcfcfc; font-family: 'Inter', sans-serif; }
    
    /* Kartice za podatke */
    .stat-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #f0f0f0;
        margin-bottom: 15px;
    }
    
    /* Customization za tabove */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #eee; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: transparent; border: none; font-weight: 500;
    }
    .stTabs [aria-selected="true"] { color: #2e7d32 !important; border-bottom: 2px solid #2e7d32 !important; }
    
    /* Gumbi */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #2e7d32;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1b5e20; border: none; }
    </style>
    """, unsafe_allow_html=True)

# Pomoćne funkcije za bazu
FILES = {"weight": "weight.csv", "food": "food_log.csv", "fast": "fast.csv"}
for f in FILES.values(): 
    if not os.path.exists(f): pd.DataFrame().to_csv(f, index=False)

# --- 2. EKSPERTNA BAZA ---
FOOD_DB = {
    "Jaja (2 kom)": {"p": 12, "f": 10, "c": 1},
    "Avokado (100g)": {"p": 2, "f": 15, "c": 2},
    "Steak (200g)": {"p": 50, "f": 30, "c": 0},
    "Maslinovo ulje (1 žlica)": {"p": 0, "f": 14, "c": 0},
    "Špinat (200g)": {"p": 6, "f": 1, "c": 2},
    "Bademi (30g)": {"p": 6, "f": 14, "c": 3}
}
