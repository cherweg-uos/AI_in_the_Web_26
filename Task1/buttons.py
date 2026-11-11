import streamlit as st
from pathlib import Path
import base64
import os


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded_img = base64.b64encode(img_bytes).decode()
    return encoded_img




if "PNGList" not in st.session_state:
    st.session_state["PNGList"] = os.listdir("Task1/cards")

columns = st.columns(13, vertical_alignment="top")

for i, col in enumerate(columns):
    for row in range(4):
        img_path = "Task1/Cards/" + st.session_state["PNGList"][i + 13 * row]
        col.image(img_path)

st.text(st.session_state["PNGList"])

