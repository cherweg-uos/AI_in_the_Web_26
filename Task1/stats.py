import streamlit as st
import pandas as pd

#gibt oben beim tab den Namen #nope gibt einfach nur überschrift, name ist in main.py
st.header("Statistics")

st.write(f"Wins: {sum(st.session_state["results"])}") # sum of all 1s
st.write(f"Looses: {len(st.session_state["results"]) - sum(st.session_state["results"])}") # Total - all 1s

st.divider()

tab_names = [f"Game {i+1}" for i, _ in enumerate(st.session_state["game_dfs"])]
tabs = st.tabs(tab_names)

for i, tab in enumerate(tabs):
    try:
        game_state = "Win" if st.session_state["results"][i] else "Loss"
    except:
        game_state = "Ongoig"
    tab.subheader(f'Game {i+1}: {game_state}')
    tab.write(st.session_state["game_dfs"][i])