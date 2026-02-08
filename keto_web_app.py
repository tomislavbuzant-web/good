# --- MENU TAB (ISPRAVLJEN) ---
with t_menu:
    p_df = load_data(PROFILE_FILE, [])
    if p_df.empty: 
        st.warning("Ispunite profil u prvom tabu kako biste vidjeli svoje makrose.")
    else:
        u = p_df.iloc[0]
        # Ponovno računanje makrosa za prikaz iznad gumba
        m = calculate_macros(u["Spol"], u["Tezina"], u["Visina"], u["Godine"], u["Aktivnost"], u["Cilj"])
        
        # --- OVDJE SU TVOJI PERSONALIZIRANI MAKROSI ---
        st.subheader(f"🎯 Tvoji ciljni makrosi ({u['Ime']})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ciljne Kalorije", f"{m['kcal']} kcal")
        c2.metric("Masti (70%)", f"{m['fat']} g")
        c3.metric("Proteini (25%)", f"{m['prot']} g")
        c4.metric("Ugljikohidrati (5%)", f"{m['carb']} g")
        
        st.divider()

        if st.button("🪄 GENERIRAJ OPTIMALNI MENU", use_container_width=True):
            combos = []
            # Algoritam testira 500 kombinacija da nađe najbolju
            for _ in range(500):
                b = random.choice([x for x in KETO_MEALS if x['type'] == "Breakfast"])
                l = random.choice([x for x in KETO_MEALS if x['type'] == "Lunch"])
                d = random.choice([x for x in KETO_MEALS if x['type'] == "Dinner"])
                s = random.choice([x for x in KETO_MEALS if x['type'] == "Snack"])
                
                tk = b['kcal'] + l['kcal'] + d['kcal'] + s['kcal']
                combos.append({
                    "meals": [b, l, d, s],
                    "total_kcal": tk,
                    "diff": abs(tk - m['kcal'])
                })
            
            # Uzimamo kombinaciju koja najmanje odstupa od cilja
            best = min(combos, key=lambda x: x['diff'])
            
            st.success(f"Pronađen meni koji troši {best['total_kcal']} kcal (Razlika: {best['total_kcal'] - m['kcal']} kcal)")
            
            labels = ["Doručak", "Ručak", "Večera", "Snack"]
            for i, meal in enumerate(best['meals']):
                header = f"{labels[i]}: {meal['name']} | 🔥 {meal['kcal']} kcal (M:{meal['fat']}g, P:{meal['prot']}g, UH:{meal['carb']}g)"
                with st.expander(header, expanded=False):
                    st.write("**🛒 Namirnice:**")
                    for ing in meal['ingredients']: st.write(f"- {ing}")
                    st.info(f"**👨‍🍳 Priprema:** {meal['preparation']}")
            
            # Donji prikaz s Deltom
            st.divider()
            tk = best['total_kcal']
            tf = sum(x['fat'] for x in best['meals'])
            tp = sum(x['prot'] for x in best['meals'])
            tc = sum(x['carb'] for x in best['meals'])
            
            res_c1, res_c2, res_c3, res_c4 = st.columns(4)
            res_c1.metric("Kcal", f"{tk}", delta=tk-m['kcal'], delta_color="inverse")
            res_c2.metric("Masti", f"{tf}g", delta=tf-m['fat'])
            res_c3.metric("Prot", f"{tp}g", delta=tp-m['prot'])
            res_c4.metric("UH", f"{tc}g", delta=tc-m['carb'], delta_color="inverse")
