import streamlit as st
import os

#laden der SVGs wenn sie noch nicht im session state gespeichert sind 
if "SVGList" not in st.session_state:
    st.session_state["SVGList"] = os.listdir("cards")

#hier wird debug auf False gestellt fals nichts eingetragen ist im session state
if "debug" not in st.session_state:
    st.session_state["debug"] = False

#hier werden die 2 Seiten die es gibt zugewiesen
gamepage = st.Page("game.py", title="Game", icon="🎮")
statspage = st.Page("stats.py", title="Stats", icon="📈")

#und hier an den rand gesetzt 
pg = st.navigation(pages=[gamepage, statspage])
pg.run()