import streamlit as st
from openai import OpenAI, AuthenticationError, OpenAIError
import random
import base64
import os 

# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    #api_key= "sk-F8IgUv-UF6tYpX_dxqxMig"
)
#das gibt den image path an 
image_path = "Task1/cards/2_of_clubs.png" 
#zum encoden zu base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
#speicher von base64 image 
base64_image = encode_image(image_path)



#Tab name 
st.header("Guessing Game")

# create list of all cards using unicode characters/ wir verwenden keine mehr right? 
deck = []
for hex in range(0x0001F0A1,0x0001F0DF):
    if (hex % 16) not in [0, 12, 15]: # who TF put mahjong tiles between the playing cards?
        deck.append(chr(hex))


# create a new random number if we don't have one yet / und ein knopf wird erstelt 
resetbuton = st.button("Reset", width="stretch", shortcut="Space")

if ("number" not in st.session_state) or resetbuton:
    st.session_state["number"] = random.randint(0,51)
    st.info("New Card Selected!")
    
if st.session_state["debug"]:
    st.text(f"The number is {st.session_state['number']}")
    st.image({"Task1/cards/" + st.session_state["SVGList"][st.session_state["number"]]}) #dateinamenliste[zufallsnummer]

with st.form("number_form"):
    guess = st.text_input("Enter Question or a Guess")
    submitted = st.form_submit_button("Submit")

if submitted:
    st.write(f"You submitted: {guess}")
    # Run your calculation or other action here.
    if guess == st.session_state['number']:
        st.success("Yeah! You did it")
        del st.session_state['number']
    else:
        st.error("Oh no. The Card is wrong.")

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

