import streamlit as st
import pandas as pd

#gibt oben beim tab den Namen #nope gibt einfach nur überschrift, name ist in main.py
st.header("Statistics")

df = pd.DataFrame(, columns=["Guess #",
                            "User Prompt",
                            "Possile Cards",
                            "Impossible Cards",
                            "Entropy",
                            "Information Gain",
                            "Quality of Guess"])

