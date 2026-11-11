import streamlit as st
import os

# 1. Load sorted filenames once into session_state
if "PNGList" not in st.session_state:
    st.session_state["PNGList"] = sorted(os.listdir("Task1/cards"))

gamepage = st.Page("grid.py", title="grid", icon="🎮")
statspage = st.Page("slider.py", title="slider", icon="📈")

#und hier an den rand gesetzt 
pg = st.navigation(pages=[gamepage, statspage])
pg.run()