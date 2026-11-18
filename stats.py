import streamlit as st
import pandas as pd

#gibt oben beim tab den Namen #nope gibt einfach nur überschrift, name ist in main.py
st.header("Statistics")

total_tab, game_tab = st.tabs(["Total", "Per Game"])

with total_tab:

    results_df = pd.DataFrame(
        {
            "Total Wins": [sum(st.session_state["results"] > 0)], # totally didn't rewrite the entire results array with np just to use masks...
            "Total Losses": [-sum(st.session_state["results"] < 0)],
        }
    )

    st.subheader("Total Wins/Losses")
    st.bar_chart(results_df, x=None, y=["Total Losses", "Total Wins"], y_label="Score", color=["red","green"], horizontal=True)
    st.dataframe(results_df, hide_index=True)

    st.divider()

    st.subheader("Number of Questions per Game")
    st.bar_chart({f"Game {i + 1}": int(g_df["Question #"].iloc[-1]) for i, g_df in enumerate(st.session_state["game_dfs"])})

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
