import streamlit as st
from st_clickable_images import clickable_images
from openai import OpenAI, AuthenticationError, OpenAIError
import random
import base64
import json 
import os 


# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key= st.session_state["AI_KEY"]
)

st.header("Guessing Game")

st.set_page_config(layout="wide")

# create a new random number if we don't have one yet / und ein knopf wird erstelt 
resetbuton = st.button("Restart the Game", width="stretch")
if resetbuton:
    st.session_state["number"] = None
    st.session_state["last_guess"] = None
    # todo: implement full reset

#falls noch keine nummer festgelegt ist wird hier random eine zwischen 0&51
if ("number" not in st.session_state) or resetbuton:
    st.session_state["number"] = random.randint(0,51)
    st.info("New Card Selected!")

# debug info for selected card
if st.session_state["debug"]:
    st.text(f"The number is #{st.session_state['number']}, which is \"{st.session_state["cards_names"][st.session_state["number"]]}\"")
    st.image(st.session_state["cards_paths"][st.session_state["number"]], width=250) #dateipfadliste[zufallsnummer]

st.subheader("Ask a LLM for hints")
prompt = st.text_area("Question to ask:")
#abrufen von base64 image 
base64_image = st.session_state["cards_base64"][st.session_state["number"]] 
if st.button("Submit", disabled=not prompt.strip()):
    try:
        with st.spinner("Answer is being created …"):
            response = client.chat.completions.create(
                model="google/gemma-4-E4B-it",
                messages=[
                   {"role": "developer", "content": "Es geht um normales 52Karten Deck. Falls nach der Farbe gefragt wird schau nach den Farben die nicht weiß sind.Es gibt nur Rote und Schwartzte Karten.Falls du dir nicht sicher bisst denke länger nahc und antworte nur mit ja oder Nein.Gebe als antwort eine Json aus. In dieser Speicherst du deine Ja nein Antwort unter Antwort. Der user soll die Karte mit Zahl/symbol eraten z.B 2 Karo oder Herz König."},
                   {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/svg+xml;base64,{base64_image}"}}],},
                   {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"})

        st.write(json.loads( response.choices[0].message.content))
    
    except AuthenticationError:
        st.error("API was not accept. Please check it.")

st.subheader("Submit Final Guess")
# clickable display of all cards
clicked = clickable_images(
    paths=st.session_state["cards_base64"],
    titles=st.session_state["cards_names"],
    div_style={"display": "grid",
               "grid-template-columns": "repeat(13, 1fr)",
               "grid-template-rows": "repeat(4, 1fr)",
               "gap": "10px",
               "max-width": "100%",
               "box-sizing": "border-box",
               "justify-content": "center"},
    img_style={"max-width": "100%", "height": "auto", "object-fit": "contain"},
)
# Submit buton displaying selected card
submit_buton_text = f"Submit **{st.session_state["cards_names"][clicked]}** as final guess" if clicked > -1 else "No Card Selected"
submitted = st.button(submit_buton_text, type="primary", disabled=(clicked <= -1), width="stretch")

if submitted:
    st.session_state["last_guess"] = clicked
    st.write(f"You submitted: {st.session_state["cards_names"][st.session_state["last_guess"]]}") # submitet gues wird nochmal angezeigt
    # Run your calculation or other action here.
    if st.session_state["last_guess"] == st.session_state['number']:
        st.success("Yeah! You did it")
        del st.session_state['number']
    else:
        st.error("Oh no. The Card is wrong.")