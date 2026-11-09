import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError
import base64
import os 

st.set_page_config(page_title="Meine KI-App")

# ── ask for API Key, stop if not yet provided  ────────────────────────────────────────────





# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key=api_key
)
#das gibt den image path an 
image_path = "cards/2_of_clubs.png" 
#zum encoden zu base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
#speicher von base64 image 
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
                   {"role": "developer", "content": "Antworte mit Ja und Nein.Gebe dazu immer noch in anführungszeichen ein zitat aus was der user gefragt hat. Es geht um normales 52Karten Deck. Falls nach der Farbe gefragt wird schau nach den Farben die nicht weiß sind.Es gibt nur Rote und Schwartzte Karten.Falls du dir nicht sicher bisst denke länger nahc und antworte nur mit ja oder Nein"},
                   {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/svg+xml;base64,{base64_image}"}}],},
                   {"role": "user", "content": prompt}
                ],
            )

        st.write(response.choices[0].message.content)

    except AuthenticationError:
        st.error("API was not accept. Please check it.")

  
