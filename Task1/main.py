import streamlit as st
import pandas as pd
from openai import OpenAI, AuthenticationError, OpenAIError
import base64
import os
import time
import math

def calculate_entropy(p_cards, i_cards) -> tuple[float, float]:
    p_hit = 1/len(p_cards)
    if p_hit == 1:
        return 0, 0
    p_miss = 1 - p_hit
    local_entropy = -(p_hit * math.log2(p_hit) + p_miss * math.log2(p_miss))
    global_entropy = (len(p_cards) / (len(p_cards) + len(i_cards)) * local_entropy)
    return local_entropy, global_entropy

st.set_page_config(layout="wide")

if "AI_KEY" in st.session_state: #search for key in session storage
    ai_key = st.session_state["AI_KEY"]
    print("Loaded AI Key from session")
elif os.path.exists(".streamlit/secrets.toml"): #search for a secrets file
    if st.secrets and "AI_KEY" in st.secrets:
        ai_key = st.secrets["AI_KEY"]
        st.session_state["AI_KEY"] = ai_key
        print("Loaded AI Key from secrets")

else: #Ask for AI key
    ai_key_input = st.text_input("Enter your AI Key:", type="password", required=True)
    if ai_key_input:
        with st.spinner("Checking AI Key", show_time=True):
            time.sleep(1)
            try:
                OpenAI(api_key=ai_key_input).models.list()
                st.session_state["AI_KEY"] = ai_key_input
                print("Loaded valid AI Key from Input")
                st.info("Valid AI Key")
                st.rerun()
            except OpenAIError:
                st.error("Invalid AI Key")
    st.stop() # make input box disappear by rerunning


# populate lists for the card filennames and paths
if "cards_names" not in st.session_state:
    st.session_state["cards_names"] = [] # start with empty lsit
    for suit in ["Clubs", "Diamonds", "Hearts", "Spades"]: # keep this order to match file order
        for rank in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]: # keep this order to match file order
            st.session_state["cards_names"].append(f"{rank} of {suit}") # add card name RANK of SUIT to list
    print(f'st.session_state["cards_names"] = {st.session_state["cards_names"]}')

# attempt to improve AI performance
if "short_cards_names" not in st.session_state:
    st.session_state["short_cards_names"] = [] # start with empty lsit
    for suit in ["C", "D", "H", "S"]: # keep this order to match file order
        for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]: # keep this order to match file order
            st.session_state["short_cards_names"].append(f"{rank}{suit}") # add card name RANK of SUIT to list
    print(f'st.session_state["short_cards_names"] = {st.session_state["short_cards_names"]}')

# populate lists for the card filennames and paths
if "cards_paths" not in st.session_state:
    st.session_state["cards_paths"] = ["Task1/cards/" + filename for filename in os.listdir("Task1/cards")] # paths created from prefix
    print(f'st.session_state["cards_paths"] = {st.session_state["cards_paths"]}')

# populate list for the cards base64 image data
if "cards_base64" not in st.session_state:
    st.session_state["cards_base64"] = [] # start with empty list
    for file in st.session_state["cards_paths"]:
        with open(file, "rb") as image: # open image file
            encoded = base64.b64encode(image.read()).decode() # encode image
            st.session_state["cards_base64"].append(f"data:image/png;base64,{encoded}") #append to list
    print(f'st.session_state["cards_base64"] = DO NOT PRINT BASE 64 IMG DATA YOU STUPID') # this will no longer spam the console


if "reset" not in st.session_state:
    st.session_state["reset"] = False

# initialize game statistics
if "g_idx" not in st.session_state:
    st.session_state["g_idx"] = 0 # zähler für spielenummer

# initialise data if we don't have history
if "q_idx" not in st.session_state:
    st.session_state["q_idx"] = 1
    st.session_state["p_cards"] = st.session_state["short_cards_names"] # all cards potenially possible
    st.session_state["i_cards"] = [] # no impossible cards

if "game_dfs" not in st.session_state:
    st.session_state["game_dfs"] = [] # hier gehöre die df's für jeden durchlauf rein
    st.session_state["game_dfs"].append(pd.DataFrame([{"Question #": 0,
                                                        "User Prompt": "",
                                                        "AI Response": "",
                                                        "Possible Cards": st.session_state["p_cards"],
                                                        "Impossible Cards": st.session_state["i_cards"],
                                                        "Global Entropy": calculate_entropy(st.session_state["p_cards"], [])[1],
                                                        "Information Gain": "",
                                                        "Quality of Guess (AI)": "",
                                                        "Quality of Guess": ""}]))
if "results" not in st.session_state:
    st.session_state["results"] = [] # liste aller ergebnisse 1 = Win, 0 = Lose


# react to clicked image
if "clicked" not in st.session_state:
    st.session_state["clicked"] = -1
if "last_guess" not in st.session_state:
    st.session_state["last_guess"] = None

#hier wird debug auf False gestellt fals nichts eingetragen ist im session state
if "debug" not in st.session_state:
    st.session_state["debug"] = False
#debugtoggel wird definiert und ein toggel wird eingeführt und der state in debug gespeichert
st.session_state["debug"] = st.sidebar.toggle("Activate Debug", st.session_state["debug"])


#hier werden die 2 Seiten die es gibt zugewiesen
gamepage = st.Page("game.py", title="Game", icon="🎮")
statspage = st.Page("stats.py", title="Stats", icon="📈")

if st.session_state["debug"] == True: 
    debug = st.Page("debug.py", title="Debug", icon="🚧")
    bug = st.navigation(pages=[gamepage, statspage,debug])
    bug.run()

else: 
#und hier an den rand gesetzt 
    pg = st.navigation(pages=[gamepage, statspage])
    pg.run()

