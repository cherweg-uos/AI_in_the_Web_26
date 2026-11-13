import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError
import base64
import os
import time



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
            except:
                st.error("Invalid AI Key")
                ai_key_input = None
    st.stop() # make input box disappear by rerunning


# populate lists for the card filennames and paths
if "cards_names" not in st.session_state:
    st.session_state["cards_names"] = [] # start with empty lsit
    for suit in ["Clubs", "Diamonds", "Hearts", "Spades"]: # keep this order to match file order
        for rank in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]: # keep this order to match file order
            st.session_state["cards_names"].append(f"{rank} of {suit}") # add card name RANK of SUIT to list
    print(f'st.session_state["cards_names"] = {st.session_state["cards_names"]}')

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

# initialize game statistics
if "g_idx" not in st.session_state:
    st.session_state["g_idx"] = 1
if "games" not in st.session_state:
    st.session_state["games"] = []
if "Wins" not in st.session_state:
    st.session_state["wins"] = 0 
if "losses" not in st.session_state:
    st.session_state["losses"] = 0

#hier wird debug auf False gestellt fals nichts eingetragen ist im session state
if "debug" not in st.session_state:
    st.session_state["debug"] = False
#debugtoggel wird definiert und ein toggel wird eingeführt und der state in debug gespeichert
st.session_state["debug"] = st.sidebar.toggle("Activate Debug", st.session_state["debug"])


#hier werden die 2 Seiten die es gibt zugewiesen
gamepage = st.Page("game.py", title="Game", icon="🎮")
statspage = st.Page("stats.py", title="Stats", icon="📈")


#und hier an den rand gesetzt 
pg = st.navigation(pages=[gamepage, statspage])
pg.run()

