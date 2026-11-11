import streamlit as st
import os


st.set_page_config(layout="wide")

# 2. State: stores the selected card as an integer index (or None)
if "selected_idx" not in st.session_state:
    st.session_state["selected_idx"] = None

# 3. Control: disable/grey out cards by their integer index (0 to 51)
with st.sidebar:
    disabled_indices = st.multiselect(
        "Grey out cards (by index):",
        options=list(range(52)),
        default=[]
    )

# 4. Display current selection
st.write(f"Selected Card Index: **{st.session_state['selected_idx']}**")

# 5. Render 4 rows x 13 columns purely by index
for row in range(4):
    cols = st.columns(13)
    for col in range(13):
        idx = row * 13 + col  # 0, 1, 2, ... 51
        
        file_path = f"Task1/cards/{st.session_state['PNGList'][idx]}"
        is_disabled = idx in disabled_indices
        is_selected = idx == st.session_state["selected_idx"]
        
        with cols[col]:
            st.image(file_path, use_container_width=True)
            
            label = "✅" if is_selected else " "
            if st.button(label, key=f"btn_{idx}", disabled=is_disabled, use_container_width=True):
                st.session_state["selected_idx"] = idx
                st.rerun()