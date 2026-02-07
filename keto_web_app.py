import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# Data files
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

# --- 2. EXTENSIVE LIBRARIES ---

# Food Database with Macros (per 100g or unit)
KETO_FOODS = {
    "Avocado": {"Fat": 15, "NetCarb": 2, "Protein": 2, "Unit": "100g"},
    "Chicken Thigh (Skin on)": {"Fat": 15, "NetCarb": 0, "Protein": 20, "Unit": "100g"},
    "Spinach": {"Fat": 0, "NetCarb": 1, "Protein": 3, "Unit": "100g"},
    "Ribeye Steak": {"Fat": 22, "NetCarb": 0, "Protein": 24, "Unit": "100g"},
    "Salmon (Fatty)": {"Fat": 13, "NetCarb": 0, "Protein": 20, "Unit": "100g"},
    "Eggs": {"Fat": 5, "NetCarb": 0.6, "Protein": 6, "Unit": "1 Large"},
    "Butter (Grass-fed)": {"Fat": 12, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
    "MCT Oil": {"Fat": 14, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
    "Bacon": {"Fat": 42, "NetCarb": 1.4, "Protein": 37, "Unit": "100g"},
    "Pecans": {"Fat": 72, "NetCarb": 4, "Protein": 9, "Unit": "100g"},
    "Zucchini": {"Fat": 0.3, "NetCarb": 2.1, "Protein": 1.2, "Unit": "100g"},
    "Heavy Cream": {"Fat": 5, "NetCarb": 0.4, "Protein": 0.4, "Unit": "1 tbsp"},
    "Parmesan Cheese": {"Fat": 28, "NetCarb": 4, "Protein": 38, "Unit": "100g"}
}

# Supplement Database with Keto/Fasting Logic
SUPPLEMENT_DB = {
    "Magnesium Glycinate": {"dose": "400mg", "timing":
