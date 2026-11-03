import streamlit as st

st.header("Statistics")

debugtoggle = st.toggle("Activate Debug", st.session_state["debug"])
st.session_state["debug"] = debugtoggle
if debugtoggle:
    st.write("Debug activated!")
