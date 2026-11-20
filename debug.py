import streamlit as st

# rint content of all session state keys exept base64 data
for key in st.session_state:
    st.divider()
    st.write(f"{key}:")
    if key == "cards_base64":
        st.write(f"*[Redacted]*")
    elif key == "game_dfs":
        for df in st.session_state["game_dfs"]:
            st.dataframe(df)
    else:
        st.write(st.session_state[key])
    

