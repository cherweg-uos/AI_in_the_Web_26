import streamlit as st
import pandas as pd
from openai import OpenAI, AuthenticationError, OpenAIError
import base64
import os
import time
import math

st.set_page_config(layout="wide")

time.sleep(1)

if "AI_KEY" in st.session_state:
    ai_key = st.session_state["AI_KEY"]
    print("Loaded AI Key from session")
elif "AI_KEY" in st.secrets:
    st.session_state["AI_KEY"] = st.secrets["AI_KEY"]
    print("Loaded AI Key from secrets")
else:
    st.info("Please enter your API Key to start.")
    with st.form("api_key_form", clear_on_submit=True):
        ai_key_input = st.text_input("Enter your AI Key:", type="password", required=True)
        submit_button = st.form_submit_button("Verify", type="primary")
        if submit_button:
            st.session_state["AI_KEY"] = ai_key_input.strip()
            print("Loaded AI Key from Input")
        else:
            st.stop()

print("Checking AI Key validity now")

if ("valid_ai_key" not in st.session_state) or (st.session_state["valid_ai_key"] == False):
    with st.spinner("Checking AI Key", show_time=True):
        time.sleep(0.1)
        try:
            OpenAI(api_key=st.session_state["AI_KEY"], base_url="https://litellm.uni-osnabrueck.de/v1").models.list()
            print("Key Valid")
            st.session_state["valid_ai_key"] = True
            st.rerun()
        except OpenAIError:
            print("Key Invalid")
            st.session_state["valid_ai_key"] = False
            del st.session_state["AI_KEY"]
            st.rerun()

# stop page and wait for input if no valid AI Key at this point
# if incorrect key in secrets.toml then ther won't be input available and page just stops
# hopefully users with .toml will be smart enough to understand, fingers crossed 
if "AI_KEY" not in st.session_state:
    st.stop() 

### -Initalisierung 
# populate lists for the card filennames and paths; important for displaying the name 
if "cards_names" not in st.session_state:
    st.session_state["cards_names"] = [] # start with empty list
    for suit in ["Clubs", "Diamonds", "Hearts", "Spades"]: # keep this order to match file order
        for rank in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]: # keep this order to match file order
            st.session_state["cards_names"].append(f"{rank} of {suit}") # add card name RANK of SUIT to list
    print(f'st.session_state["cards_names"] = {st.session_state["cards_names"]}')

# populate list for the cards base64 image data
if "cards_base64" not in st.session_state:
    st.session_state["cards_base64"] = [] # start with empty list
    for file in ["cards/" + img for img in os.listdir("cards")] :
        with open(file, "rb") as image: # open image file
            encoded = base64.b64encode(image.read()).decode() # encode image
            st.session_state["cards_base64"].append(f"data:image/png;base64,{encoded}") #append to list
    print(f'st.session_state["cards_base64"] = DO NOT PRINT BASE 64 IMG DATA YOU STUPID') # this will no longer spam the console



if "reset" not in st.session_state:
    st.session_state["reset"] = False

# initialize game statistics
if "g_idx" not in st.session_state:
    st.session_state["g_idx"] = 0 # zähler für spielenummer

# initialize data if we don't have history
if "q_idx" not in st.session_state:
    st.session_state["q_idx"] = 1
    

if "game_dfs" not in st.session_state:
    st.session_state["game_dfs"] = [] # hier gehöre die df's für jeden durchlauf rein
    st.session_state["game_dfs"].append(pd.DataFrame([{"Question #": 0,
                                                        "User Prompt": "",
                                                        "AI Response": "",
                                                        "Quality of Guess (AI)": "",
                                                        "Quality of Guess": ""
                                                        }]))
if "results" not in st.session_state:
    st.session_state["results"] = [] # liste aller ergebnisse 1 = Win, 0 = Lose


# react to clicked image
if "clicked" not in st.session_state:
    st.session_state["clicked"] = -1
if "last_guess" not in st.session_state:
    st.session_state["last_guess"] = None

if "messages" not in st.session_state:
    st.session_state.messages = []

#hier wird debug auf False gestellt fals nichts eingetragen ist im session state
if "debug" not in st.session_state:
    st.session_state["debug"] = False
#debugtoggel wird definiert und ein toggel wird eingeführt und der state in debug gespeichert
st.session_state["debug"] = st.sidebar.toggle("Activate Debug", st.session_state["debug"])


#hier werden die 2 Seiten die es gibt zugewiesen
gamepage = st.Page("game.py", title="Game", icon="🎮")
statspage = st.Page("stats.py", title="Stats", icon="📈")

#bei debug true die debug seite anzeigen 
if st.session_state["debug"] == True: 
    debug = st.Page("debug.py", title="Debug", icon="🚧")
    bug = st.navigation(pages=[gamepage, statspage,debug])
    bug.run()

else: 
#und hier an den rand gesetzt 
    pg = st.navigation(pages=[gamepage, statspage])
    pg.run()

