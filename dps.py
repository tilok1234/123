import streamlit as st

st.set_page_config(page_title="DPS Calculator")

st.title("⚔️ DPS Calculator")

min_damage = st.number_input("Min Damage", value=1076.0)
max_damage = st.number_input("Max Damage", value=1686.0)
attack_speed = st.number_input("Attack Speed", value=2.6)
crit_chance = st.number_input("Crit Chance (%)", value=77.03)
crit_multiplier = st.number_input("Crit Multiplier", value=2.0)

if st.button("Calculate DPS"):
    crit_chance /= 100
    avg_damage = (min_damage + max_damage) / 2
    base_dps = avg_damage * attack_speed
    effective_multiplier = (1 - crit_chance) + (crit_chance * crit_multiplier)
    final_dps = base_dps * effective_multiplier

    st.success(f"🔥 DPS: {final_dps:.2f}")