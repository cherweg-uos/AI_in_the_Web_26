import streamlit as st

# A horizontal slider from 0 to 51
card_idx = st.select_slider(
    "Slide to pick a card:",
    options=list(range(52)),
    value=st.session_state.get("selected_idx", 0)
)

st.session_state["selected_idx"] = card_idx

# Show the chosen card prominently
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.image(f"Task1/cards/{st.session_state['PNGList'][card_idx]}", caption=f"Card Index: {card_idx}", use_container_width=True)