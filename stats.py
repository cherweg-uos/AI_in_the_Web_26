import streamlit as st
import pandas as pd
import numpy as np
from statistics import mean

#gibt oben beim tab den Namen #nope gibt einfach nur überschrift, name ist in main.py
st.header("Statistics")

total_tab, game_tab = st.tabs(["Total", "Per Game"])

with total_tab:

    results_df = pd.DataFrame(
        {
            "Total Wins": [sum(st.session_state["results"] > 0)], # totally didn't rewrite the entire results array with np just to use masks...
            "Total Losses": [-sum(st.session_state["results"] < 0)],
            "Games Finished": [len(st.session_state["game_dfs"])-1],
            "Avg. Questions per Game": [mean([g_df["Question #"].iloc[-1] for g_df in st.session_state["game_dfs"]])],
        }
    )

    st.subheader("Total Wins/Losses")
    st.bar_chart(results_df, x=None, y=["Total Losses", "Total Wins"], y_label="Score", color=["red","green"], horizontal=True)
    st.dataframe(results_df, hide_index=True)

    st.divider()

    st.subheader("Number of Questions per Game")
    st.bar_chart({f"Game {i + 1}": int(g_df["Question #"].iloc[-1]) for i, g_df in enumerate(st.session_state["game_dfs"])})

    if "c" not in st.session_state: # i hate this
        st.session_state["c"] = 0
    # take new cumsum if closer to 0, else take previous cumsum 
    offset = [c if abs(c := c + r) < abs(c - r) else c - r for r in st.session_state["results"]] 
    st.bar_chart(
        {
            "Offset": offset,
            "Wins": [r if r > 0 else 0 for r in st.session_state["results"]],
            "Losses": [r if r < 0 else 0 for r in st.session_state["results"]],
        }, 
        color=["#0000", "green", "red"]
    )

with game_tab:
    st.write("Select Game:")
    idx = st.pagination(len(st.session_state["game_dfs"]))
    # when populating page, add correct result to Header
    try:
        match st.session_state["results"][idx - 1]:
            case 1:
                game_state = "Win"
            case 0:
                game_state = "Reset"
            case -1:
                game_state = "Loss"
    except:
        game_state = "Unfinished"
    st.subheader(f'Game {idx}: {game_state}')
    st.dataframe(st.session_state["game_dfs"][idx - 1], hide_index=True)
