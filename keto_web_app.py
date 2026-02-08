import streamlit as st
import datetime
import pandas as pd

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Keto Intelligence Pro", page_icon="🥑", layout="wide")

# --- 2. JEDNOSTAVAN I ČIST DIZAJN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { font-size: 2rem; color: #2e7d32; }
    .stButton>button {
        border-radius: 8px;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    .status-box {
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        border: 1px solid #eee;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DASHBOARD PODACI ---
if 'weight' not in st.session_state: st.session_state.weight = 85.0
if 'fasting_active' not in st.session_state: st.session_state.fasting_active = False

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🥑 Keto Pro")
    st.markdown("---")
    st.session_state.weight = st.number_input("Trenutna težina (kg)", 40.0, 200.0, st.session_state.weight)
    st.info("Sustav: Metrički | Celsius")
    st.markdown("---")
    st.write("💡 **Keto podsjetnik:** Pij dovoljno vode s elektrolitima!")

# --- 5. GLAVNI EKRAN ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🍽️ Prehrana", "🧪 Biomarkeri"])

with tab1:
    st.subheader("Dobro jutro! ☀️")
    
    # Glavne metrike u redu
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Težina", f"{st.session_state.weight} kg", "-0.5 kg")
    with col2:
        st.metric("Vrijeme posta", "14:20 h")
    with col3:
        st.metric("Unos vode", "2.2 L", "💧")

    st.markdown("---")
    st.subheader("Status posta")
    if not st.session_state.fasting_active:
        if st.button("🚀 Započni novi post"):
            st.session_state.fasting_active = True
            st.rerun()
    else:
        st.warning("Trenutno si u stanju posta. Tijelo koristi vlastite masne zalihe.")
        if st.button("🍽️ Završi post"):
            st.session_state.fasting_active = False
            st.balloons()
            st.rerun()

with tab2:
    st.subheader("Dnevni Makrosi")
    
    # Vizualni prikaz progresa
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("🥩 Proteini")
        st.progress(0.4)
        st.caption("40g / 100g")
    with c2:
        st.write("🥑 Masti")
        st.progress(0.7)
        st.caption("105g / 150g")
    with c3:
        st.write("🥦 Neto UH")
        st.progress(0.15)
        st.caption("3g / 20g")

    st.markdown("---")
    st.write("🔍 **Brzi izračun obroka**")
    food = st.selectbox("Što jedeš?", ["Jaja sa slaninom", "Odrezak i špinat", "Avokado i losos"])
    if st.button("Dodaj u dnevnik"):
        st.success(f"Dodano: {food}!")

with tab3:
    st.subheader("Metabolička analiza")
    col_a, col_b = st.columns(2)
    
    with col_a:
        glu = st.number_input("Glukoza (mmol/L)", 3.0, 10.0, 4.8)
        ket = st.number_input("Ketoni (mmol/L)", 0.0, 7.0, 1.5)
        
    with col_b:
        gki = glu / ket if ket > 0 else 0
        st.metric("GKI Index", f"{gki:.2f}")
        
        if gki < 3:
            st.success("Stanje: Terapeutska ketoza")
        elif gki < 9:
            st.info("Stanje: Optimalno sagorijevanje masti")
        else:
            st.warning("Stanje: Izvan ketoze")



st.markdown("---")
st.caption("Keto Intelligence Pro • 2026")
