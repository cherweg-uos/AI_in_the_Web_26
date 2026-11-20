import streamlit as st
import pandas as pd
from statistics import mean

# Title
st.header("Statistics")

# Subdivision for total statistics
st.divider()
st.subheader("Total")

# create df with total game statistics
total_results_df = pd.DataFrame(
    {
        "Total Wins": [sum([1 for x in st.session_state["results"] if x == 1])],
        "Total Losses": [sum([-1 for x in st.session_state["results"] if x == -1 ])],
        "Games Finished": [len(st.session_state["game_dfs"])-1],
        "Avg. Questions per Game": [mean([g_df["Question #"].iloc[-1] for g_df in st.session_state["game_dfs"]])],
    }
)
# horizontal bar chart displaying win loss ratio
st.bar_chart(total_results_df, x=None, y=["Total Losses", "Total Wins"], y_label="Score", color=["red","green"], horizontal=True)

# display df to show statistics
st.dataframe(total_results_df, hide_index=True)

st.subheader("Number of Questions per Game")

# bar chart showing the last question index for each game
st.bar_chart({f"Game {i + 1}": int(g_df["Question #"].iloc[-1]) for i, g_df in enumerate(st.session_state["game_dfs"])})

# tabs for statistics per game
tab_names = [f"Game {i+1}" for i, _ in enumerate(st.session_state["game_dfs"])]
tabs = st.tabs(tab_names)

# populate each tab with with "game index : state" and it's corresponding game df
for i, tab in enumerate(tabs):
    try:
        match st.session_state["results"][i]:
            case 1:
                game_state = "Win"
            case 0:
                game_state = "Reset"
            case -1:
                game_state = "Loss"
    except:
        game_state = "Unfinished"
    tab.subheader(f'Game {i+1}: {game_state}')
    tab.write(st.session_state["game_dfs"][i])