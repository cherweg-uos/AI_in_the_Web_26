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

    # here was supposed to be a waterfall chart of score progression, that was supposed to be achived by calculating a offset from previous cumsum and new cumsum 
    # but I also need to flip the sing of certain values for the stack to apper correcty, and for that I need to know the direction I come from.
    # all would have been so easy if only I could have -0, but alas everything just exploded into bloat
    # yes, i know waterfall charts are within streamlit, but outside of my personal library knowledge

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
