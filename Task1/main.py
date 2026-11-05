import streamlit as st
import os


if "AI_KEY" in st.secrets:
    st.session_state["AI_KEY"] = st.secrets["AI_KEY"]
    print("Loaded AI Key from secrets")
elif "AI_KEY" in st.session_state:
    print("Loaded AI Key from session")
else: #Ask for AI key
    ai_key_input = st.sidebar.text_input("Enter your AI Key:", type="password")
    if ai_key_input:
        st.session_state["AI_KEY"] = ai_key_input #idk if this is safe, need to ask in walk in session
        print("Loaded AI Key from Input") 
        st.rerun() # make input box disappear by rerunning
    
    #todo: maybe figure out how to save key back into secrets
    #or don't cause it probaly won't work in deployment enviroment anyway ¯\_(ツ)_/¯

#laden der SVGs wenn sie noch nicht im session state gespeichert sind 
if "SVGList" not in st.session_state:
    st.session_state["SVGList"] = os.listdir("Task1/cards")

#hier wird debug auf False gestellt fals nichts eingetragen ist im session state
if "debug" not in st.session_state:
    st.session_state["debug"] = False

#hier werden die 2 Seiten die es gibt zugewiesen
gamepage = st.Page("game.py", title="Game", icon="🎮")
statspage = st.Page("stats.py", title="Stats", icon="📈")

#und hier an den rand gesetzt 
pg = st.navigation(pages=[gamepage, statspage])
pg.run()

