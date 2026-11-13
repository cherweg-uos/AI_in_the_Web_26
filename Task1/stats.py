import streamlit as st
import pandas as pd

#gibt oben beim tab den Namen #nope gibt einfach nur überschrift, name ist in main.py
st.header("Statistics")

game_history_df = pd.DataFrame(columns=["Question #",
                                "User Prompt",
                                "Possible Cards",
                                "Impossible Cards",
                                "Entropy",
                                "Information Gain",
                                "Quality of Guess"])
st.session_state["game_history"] = game_history_df

st.write(f"Looses: {st.session_state["loose"]}")
st.write(f"Wins: {st.session_state["Wins"]}")