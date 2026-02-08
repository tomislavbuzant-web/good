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

    "Parmesan Cheese": {"Fat": 28, "NetCarb": 4, "Protein": 38, "Unit": "100g"}

}



SUPPLEMENT_DB = {

    "Magnesium Glycinate": {"dose": "400mg", "timing": "30 mins before Bed", "logic": "Prevents leg cramps and improves sleep."},

    "Potassium Chloride": {"dose": "1000mg", "timing": "With food", "logic": "Prevents 'Keto Flu' fatigue."},

    "Sodium (Sea Salt)": {"dose": "2-3g extra", "timing": "During Fasting", "logic": "Prevents headaches while fasting."},

    "Omega-3 (Fish Oil)": {"dose": "2000mg", "timing": "With fattiest meal", "logic": "Reduces inflammation."},

    "Vitamin D3 + K2": {"dose": "5000 IU", "timing": "Morning with fat", "logic": "Critical for hormone health."},

    "Apple Cider Vinegar": {"dose": "1 tbsp in water", "timing": "Before meals", "logic": "Improves insulin sensitivity."}

}



RECIPES_DB = [

    {

        "name": "Crispy Salmon & Asparagus",

        "fridge": ["Salmon (Fatty)", "Butter"],

        "buy": ["Asparagus", "Lemon", "Garlic"],

        "instructions": "Sear salmon in butter for 4 mins skin-side down at 200°C. Sauté asparagus in the same pan.",

        "links": ["https://www.dietdoctor.com/recipes/baked-salmon-with-asparagus", "https://www.youtube.com/results?search_query=keto+salmon+asparagus"]

    },

    {

        "name": "Keto Ribeye Feast",

        "fridge": ["Ribeye Steak", "Butter"],

        "buy": ["Fresh Rosemary", "Broccoli", "Garlic"],

        "instructions": "High heat sear (220°C). Baste with butter, rosemary, and garlic. Serve with steamed broccoli.",

        "links": ["https://www.delish.com/cooking/recipe/steak-keto", "https://www.youtube.com/results?search_query=perfect+keto+ribeye"]

    },

    {

        "name": "Bacon & Egg Avocado Bowls",

        "fridge": ["Eggs", "Bacon", "Avocado"],

        "buy": ["Chives", "Black Pepper"],

        "instructions": "Halve avocado, crack egg in center. Bake at 200°C for 15 mins. Top with crispy bacon.",

        "links": ["https://www.allrecipes.com/recipe/244257/baked-eggs-in-avocado/", "https://www.youtube.com/results?search_query=keto+avocado+egg+boats"]

    }

]



# --- 3. APP INTERFACE ---



st.title("🥑 Keto Intelligence Pro")



tab1, tab2, tab3, tab4 = st.tabs(["🕒 Fasting", "🥗 Food & Recipes", "💊 Supplements", "📈 Progress"])



# --- TAB 1: FASTING ---

with tab1:

    st.header("16/8 Fasting Tracker")

    if 'start_time' not in st.session_state:

        st.session_state.start_time = None

    

    c1, c2 = st.columns(2)

    with c1:

        if st.button("🚀 Start Fast"):

            st.session_state.start_time = datetime.datetime.now()

    with c2:

        if st.button("🍽️ End & Log"):

            if st.session_state.start_time:

                duration = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600

                new_fast = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Hours": [round(duration, 2)]})

                save_data(pd.concat([load_data(FAST_FILE, ["Date", "Hours"]), new_fast]), FAST_FILE)

                st.session_state.start_time = None

                st.success(f"Logged {duration:.1f} hours!")



    if st.session_state.start_time:

        elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds() / 3600

        st.metric("Current Timer", f"{elapsed:.1f} hrs")

        st.progress(min(elapsed/16, 1.0))

    

    st.subheader("📜 History")

    st.dataframe(load_data(FAST_FILE, ["Date", "Hours"]).tail(5), use_container_width=True)



# --- TAB 2: FOOD & RECIPES ---

with tab2:

    st.header("Keto Food Library")

    search_food = st.multiselect("Select items in your fridge:", list(KETO_FOODS.keys()))

    

    shopping_list = []



    if search_food:

        st.write("### 📊 Macros")

        for f in search_food:

            m = KETO_FOODS[f]

            st.caption(f"**{f}**: {m['Fat']}g Fat | {m['NetCarb']}g Carbs | {m['Protein']}g Protein")

        

        st.divider()

        st.header("🍳 Recommended Recipes")

        for r in RECIPES_DB:

            if any(item in search_food for item in r['fridge']):

                with st.expander(f"⭐ {r['name']}"):

                    st.write(f"**📝 Steps:** {r['instructions']}")

                    st.write(f"**🛒 Need to buy:** {', '.join(r['buy'])}")

                    shopping_list.extend(r['buy'])

                    for link in r['links']:

                        st.write(f"- [Video/Guide]({link})")

        

        if shopping_list:

            st.divider()

            st.subheader("🛒 Automatic Shopping List")

            unique_items = list(set(shopping_list))

            for item in unique_items:

                st.write(f"- [ ] {item}")



# --- TAB 3: SUPPLEMENTS ---

with tab3:

    st.header("Supplement Protocol")

    my_stack = st.multiselect("Add to your daily stack:", list(SUPPLEMENT_DB.keys()))

    

    for s in my_stack:

        data = SUPPLEMENT_DB[s]

        with st.expander(f"💊 {s}"):

            st.write(f"**Dosage:** {data['dose']}")

            st.write(f"**Timing:** {data['timing']}")

            st.info(f"**Logic:** {data['logic']}")



# --- TAB 4: PROGRESS ---

with tab4:

    st.header("Weight Tracker (kg)")

    w_val = st.number_input("Enter kg", min_value=30.0, step=0.1)

    if st.button("Save Weight"):

        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight_kg": [w_val]})

        save_data(pd.concat([load_data(WEIGHT_FILE, ["Date", "Weight_kg"]), new_w]), WEIGHT_FILE)

    

    df_w = load_data(WEIGHT_FILE, ["Date", "Weight_kg"])

    if not df_w.empty:

        df_w['Date'] = pd.to_datetime(df_w['Date'])

        st.line_chart(df_w.set_index("Date"))
