import streamlit as st
import os

if "SVGList" not in st.session_state:
    st.session_state["SVGList"] = os.listdir("cards")

if "debug" not in st.session_state:
    st.session_state["debug"] = False

gamepage = st.Page("game.py", title="Game", icon="🎮")
statspage = st.Page("stats.py", title="Stats", icon="📈")

pg = st.navigation(pages=[gamepage, statspage])
pg.run()