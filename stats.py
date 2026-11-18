import streamlit as st
import pandas as pd

#gibt oben beim tab den Namen #nope gibt einfach nur überschrift, name ist in main.py
st.header("Statistics")
st.divider()
st.subheader("Total")

results_df = pd.DataFrame(
    {
        "Wins": [1 if x == 1 else 0 for x in st.session_state["results"]],
        "Losses": [-1 if x == -1 else 0 for x in st.session_state["results"]],
    }
)
results_df.index += 1 # shift game indices by one for display

total_results_df = pd.DataFrame(
    {
        "Total Wins": [sum(results_df["Wins"])],
        "Total Losses": [sum(results_df["Losses"])],
    }
)

st.bar_chart(total_results_df, x=None, y=["Total Losses", "Total Wins"], y_label="Score", color=["red","green"], horizontal=True)

st.dataframe(total_results_df, hide_index=True)

st.subheader("Number of Questions per Game")
st.bar_chart({f"Game {i + 1}": int(g_df["Question #"].iloc[-1]) for i, g_df in enumerate(st.session_state["game_dfs"])})



tab_names = [f"Game {i+1}" for i, _ in enumerate(st.session_state["game_dfs"])]
tabs = st.tabs(tab_names)

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

    #?