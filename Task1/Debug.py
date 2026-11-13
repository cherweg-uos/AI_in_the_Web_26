import streamlit as st

st.write(st.session_state["AI_KEY"])
st.write(st.session_state["cards_names"])
st.write(st.session_state["cards_paths"])

st.write(st.session_state["g_idx"])
st.write(st.session_state["games"])
st.write(st.session_state["wins"])
st.write(st.session_state["losses"])
st.write(st.session_state["q_idx"])
st.write(st.session_state["p_cards"])
st.write(st.session_state["i_cards"])
st.write(st.session_state["clicked"])
st.write(st.session_state["debug"] )