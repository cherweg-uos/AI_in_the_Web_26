import streamlit as st
import pandas as pd
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

# initialise data if we don't have history to send
if "q_idx" not in st.session_state:
    st.session_state["q_idx"] = 0 # question 0 = before first question
    st.session_state["p_cards"] = ["cards_names"] # all cards potenially possible
    st.session_state["i_cards"] = [] # no impossible cards


st.subheader("Ask a LLM for hints")
prompt = st.text_area("Question to ask:")
#abrufen von base64 image 
base64_image = st.session_state["cards_base64"][st.session_state["number"]]
if st.button("Submit", disabled=not prompt.strip()):
    try:
        with st.spinner("Answer is being created …"):
            response = client.chat.completions.create(
                model="google/gemma-4-E4B-it",
                messages=[{"role": "developer", "content": f"""
                You are responsible for answering the user questions in a card guessing game.
                The user has to guess a random playing card out of a french 52 card deck.
                The target card the user is trying to find is provided in the image in this conversation.
                Current Game State:
                - Question Number: {st.session_state["q_idx"]}
                - Possible Cards: {st.session_state["p_cards"]}
                - Impossible Cards: {st.session_state["i_cards"]}

                Try to answer in an efficient and analytical manner. If something is not clear or concise, instead of guessing just stop and state so in the remarks. 

                For your responses always return a JSON object with the following keys:
                1. "remark" : A sarcastic comment of your choice. If you encounter any errors or are missing things, this is where to put them.
                2. "yn_response" : A Yes/No response to the user Question.
                3. "p_cards" : Updated list of remaining possile Cards based on the answer. (from the User's perspective)
                4. "i_cards" : Updated list of all impossible Cards that are now excluded by the answer. (from the User's perspective)
                5. "entropy" : The new entropy of the Possible Cards.
                6. "ig" : The information gain of the user's last question.
                7. "quality": A metric for the quality of the user question (0 to 100)."""},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": base64_image}}],},
                    {"role": "user", "content": prompt}
                   ],
                response_format={"type": "json_object"})

        ai_data = json.loads(response.choices[0].message.content)
        st.session_state["q_idx"] += 1
        st.session_state["yn_response"] = ai_data.get("yn_response")
        st.session_state["remark"] = ai_data.get("remark")
        st.session_state["p_cards"] = ai_data.get("p_cards")
        st.session_state["i_cards"] = ai_data.get("i_cards")
        st.session_state["entropy"] = ai_data.get("entropy")
        st.session_state["ig"] = ai_data.get("ig")
        st.session_state["quality"] = ai_data.get("quality")
        if st.session_state["debug"]:
            st.write(ai_data)
        st.write(ai_data["yn_response"])
    
    except AuthenticationError:
        st.error("API was not accept. Please check it.")

st.subheader("Submit Final Guess")
# clickable display of all cards
st.session_state["clicked"] = clickable_images(
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

if "clicked" not in st.session_state:
    st.session_state["clicked"] = -1
# Submit buton displaying selected card
submit_buton_text = f"Submit **{st.session_state["cards_names"][st.session_state["clicked"]]}** as final guess" if st.session_state["clicked"] > -1 else "No Card Selected"
submitted = st.button(submit_buton_text, type="primary", disabled=(st.session_state["clicked"] <= -1), width="stretch")
 
if "loose" not in st.session_state:
    st.session_state["loose"] = 0
if "Wins" not in st.session_state:
    st.session_state["Wins"] = 0 

if submitted:
    st.session_state["last_guess"] = st.session_state["clicked"]
    st.write(f"You submitted: {st.session_state["cards_names"][st.session_state["last_guess"]]}") # submitet gues wird nochmal angezeigt
    # Run your calculation or other action here.
    if st.session_state["last_guess"] == st.session_state['number']:
        st.success("Yeah! You did it")
        st.balloons()
        del st.session_state['number']
        st.session_state["Wins"] = st.session_state["Wins"] + 1
    else:
        st.error("Oh no. The Card is wrong.")
        st.session_state["loose"] = st.session_state["loose"] + 1 
      
        
