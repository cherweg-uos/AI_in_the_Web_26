import streamlit as st

#gibt oben beim tab den Namen
st.header("Statistics")

#debugtoggel wird definiert und ein toggel wird eingeführt 
debugtoggle = st.toggle("Activate Debug", st.session_state["debug"])
#und es wird der state in debug gespeichert
st.session_state["debug"] = debugtoggle

#debugtoggel scheint es zu sein wenn es na ist ? 
if debugtoggle:
    st.write("Debug activated!")
