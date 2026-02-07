import streamlit as st
import datetime
import pandas as pd
import os

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

FAST_FILE = "fasting_history.csv"
WEIGHT_FILE = "weight_history.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, columns):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame(columns=columns)

# --- 2. LIBRARIES (Data Bases) ---
KETO_FOODS = {
    "Avocado": {"Fat": 15, "NetCarb": 2, "Protein": 2, "Unit": "100g"},
    "Chicken Thigh": {"Fat": 9, "NetCarb": 0, "Protein": 24, "Unit": "100g"},
    "Spinach": {"Fat": 0, "NetCarb": 1, "Protein": 3, "Unit": "100g"},
    "Ribeye Steak": {"Fat": 22, "NetCarb": 0, "Protein": 24, "Unit": "100g"},
    "Salmon": {"Fat": 13, "NetCarb": 0, "Protein": 20, "Unit": "100g"},
    "Eggs": {"Fat": 5, "NetCarb": 0.6, "Protein": 6, "Unit": "1 Large"},
    "Butter": {"Fat": 12, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
    "MCT Oil": {"Fat": 14, "NetCarb": 0, "Protein": 0, "Unit": "1 tbsp"},
}

SUPPLEMENT_DB = {
    "Magnesium Citrate": {"dose": "400mg", "timing": "Before Bed", "benefit": "Sleep & Muscle Cramps"},
    "Potassium Chloride": {"dose": "1000mg", "timing": "With Meal", "benefit": "Keto Flu Prevention"},
    "Omega-3 Fish Oil": {"dose": "2000mg", "timing": "With Fat Meal", "benefit": "Heart & Inflammation"},
    "Vitamin D3": {"dose": "5000 IU", "timing": "Morning", "benefit": "Immune & Mood"},
    "Electrolyte Powder": {"dose": "1 scoop", "timing": "During Fasting", "benefit": "Energy & Hydration"},
    "Creatine": {"dose": "5g", "timing": "Anytime", "benefit": "Muscle Retention"},
}

RECIPES_DB = [
    {
        "name": "Crispy Salmon & Asparagus",
        "fridge": ["Salmon", "Butter"],
        "buy": ["Asparagus", "Lemon"],
        "instructions": "Sear salmon in butter for 4 mins skin-side down. Sauté asparagus in the same pan.",
        "links": ["https://www.dietdoctor.com/recipes/baked-salmon-with-asparagus", "https://youtu.be/salmon-video-1"]
    },
    {
        "name": "Keto Ribeye Feast",
        "fridge": ["Ribeye Steak", "Butter"],
        "buy": ["Garlic", "Rosemary", "Broccoli"],
        "instructions": "High heat sear for 3 mins per side. Baste with garlic butter.",
        "links": ["https://www.delish.com/cooking/recipe/steak-keto", "https://youtu.be/steak-video-1"]
    }
]

# --- 3. FASTING HISTORY LOGIC ---
st.title("🥑 Keto Intelligence Pro")

tab1, tab2, tab3, tab4 = st.tabs(["🕒 Fasting & History", "🥗 Food & Recipes", "💊 Supplements", "📈 Weight"])

with tab1:
    st.header("16/8 Intermittent Fasting")
    if 'start_time' not in st.session_state
