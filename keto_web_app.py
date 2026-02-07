import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# Corrected parameter: unsafe_allow_html for Streamlit compatibility
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

# File Management
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

# --- 2. KETO FOOD DATABASE (USDA-BASED) ---
USDA_KETO = {
    "Ribeye Steak (100g)": {"fat": 22, "prot": 24, "carb": 0, "cal": 290},
    "Eggs (Large)": {"fat": 5, "prot": 6, "carb": 0.6, "cal": 70},
    "Grass-fed Butter (15g)": {"fat": 12, "prot": 0.1, "carb": 0, "cal": 100},
    "Salmon (100g)": {"fat": 13, "prot": 20, "carb": 0, "cal": 200},
    "Avocado (Medium)": {"fat": 21, "
