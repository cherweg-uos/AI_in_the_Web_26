import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError
import base64
import os 

st.set_page_config(page_title="Meine KI-App")

# ── ask for API Key, stop if not yet provided  ────────────────────────────────────────────
with st.sidebar:
    api_key = st.text_input(
        "UOS AI API-Key",
        type="password",
        key="uos_api_key",
        placeholder="sk-...",
    ).strip()

if not api_key:
    st.info("Please enter your Uni Osnabrück API key. If you don't have one, you can obtain it from https://ai-keys.uni-osnabrueck.de.")
    st.stop()

# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key=api_key
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Path to your image
image_path = "2_of_clubs.svg"

# Getting the Base64 string
base64_image = encode_image(image_path)


# ── Main program logic starts here ────────────────────
st.title("My AI App")

prompt = st.text_area("Your Question")

if st.button("Submit", disabled=not prompt.strip()):
    try:
        with st.spinner("Answer is being created …"):
            response = client.chat.completions.create(
                model="google/gemma-4-E4B-it",
                messages=[
                   {"role": "developer", "content": "Antworte nur mit Ja oder Nein"},
                   {"role": "developer", "content": [
                       {"type": "input_image","image_url":f"data:image/jpeg;base64,{base64_image}"
                       }
                   ],
                   }
                ],
            )

        st.write(response.choices[0].message.content)

    except AuthenticationError:
        st.error("API was not accept. Please check it.")

  
