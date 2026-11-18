import streamlit as st
import pandas as pd
import numpy as np
from st_clickable_images import clickable_images
from openai import OpenAI, AuthenticationError, OpenAIError
import random
import base64
import json 
import time
import os 



# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key= st.session_state["AI_KEY"]
)

st.title("Card Guessing Game", text_alignment="center")


# function to call when resetting the game
def game_reset() -> None:
    st.session_state["number"] = random.randint(0,51) # remove selected cart
    st.session_state["last_guess"] = None # remove last guess
    st.session_state["q_idx"] = 0 # reset question index
    st.session_state["g_idx"] += 1 # increase the game index
    st.session_state["messages"] = []
    st.session_state["game_dfs"].append(pd.DataFrame([{"Question #": 0,
                                                        "User Prompt": "",
                                                        "AI Response": "",
                                                        "Global Entropy": round(np.log2(52), 2),
                                                        "Information Gain": "",
                                                        "Quality of Guess (AI)": "",
                                                        "Quality of Guess": ""}])) # add new game df to game_dfs
    st.session_state["reset"] = True
    st.rerun()

# function to calculate entropy
def calculate_entropy(p_cards, deck_size=52) -> float:
    n = len(p_cards)
    global_entropy = np.log2(n)
    return round(global_entropy, 2)

def calculate_ig(p_cards, deck_size=52) -> float:
    n = len(p_cards)
    p = n / deck_size
    ig = -p * np.log2(p) - (1-p) * np.log2(1-p)
    return round(ig, 2)

if st.session_state["reset"]:
    st.info("Game has been Reset")
    st.session_state["reset"] = False

# function to convert text into word stream
def stream_text(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)

# create a new random number if we don't have one yet / und ein knopf wird erstelt 
resetbuton = st.button("Restart the Game", width="stretch")
if resetbuton:
    st.session_state["results"].append(0)
    game_reset()

#falls noch keine nummer festgelegt ist wird hier random eine zwischen 0 and 51
if ("number" not in st.session_state) or resetbuton:
    st.session_state["number"] = random.randint(0,51)
    
# debug info for selected card
if st.session_state["debug"]:
    st.sidebar.divider()
    st.sidebar.text(f"The Card is #{st.session_state['number']}, which is \"{st.session_state["cards_names"][st.session_state["number"]]}\"")
    st.sidebar.image(st.session_state["cards_paths"][st.session_state["number"]], width=250) #dateipfadliste[zufallsnummer]

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

# Submit buton naming selected card
submit_buton_text = f"Submit **{st.session_state["cards_names"][st.session_state["clicked"]]}** as final guess" if st.session_state["clicked"] > -1 else "No Card Selected"
submitted = st.button(submit_buton_text, type="primary", disabled=(st.session_state["clicked"] <= -1), width="stretch")
 
# check if guess is correct
if submitted:
    st.session_state["last_guess"] = st.session_state["clicked"]
    st.write(f"You submitted: {st.session_state["cards_names"][st.session_state["last_guess"]]}") # submitet gues wird nochmal angezeigt
    # Run your calculation or other action here.
    if st.session_state["last_guess"] == st.session_state['number']:
        st.success("Yeah! You did it")
        st.balloons()
        del st.session_state['number']
        np.append(st.session_state["results"], 1)
    else:
        st.error("Oh no. The Card is wrong.")
        np.append(st.session_state["results"], -1)
    with st.spinner("Game is being reset …"):
        time.sleep(2) # wait a bit before forced reset
        game_reset() #forced reset so you can't add guesses once the game is over
        
st.divider()

st.subheader("Ask a LLM for hints")

chat_container = st.container(border=True)
# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with chat_container.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state["messages"]: # if there is nothing in chat history
    with chat_container.chat_message("assistant"):
        welcome_message = st.write_stream(stream_text("""
        Hello  \n
        I am your Game Master for this Card Guessing Game  \n
        I have now selected a random card out of the ones you can see above.  \n
        Your Task is to guess which one it is.  \n
        You get to ask me 5 Questions rgarding the Target card, which I will then Answer with Yes or No.
        """))
    st.session_state["messages"].append({"role": "assistant", "content": welcome_message})

chat_container.divider()

if user_prompt := st.chat_input("Question to ask: (Responses will be Yes/No only)", submit_mode="disable"):
    with chat_container.chat_message("user"): # in a user side chat bubble
        st.markdown(user_prompt) # display the prompt
    st.session_state["messages"].append({"role": "user", "content": user_prompt}) # Add user_prompt to chat history
    
    # generate new system promt
    system_prompt = f"""
    You are a strict, infallible referee for a 52-card guessing game.
    Target Card in Image: {st.session_state["cards_names"][st.session_state["number"]]} ({st.session_state["short_cards_names"][st.session_state["number"]]})
    Current Remaining Candidates: {st.session_state["p_cards"]}

    Rules:
    1. "thought": In exactly 1 short sentence briefly analyze if the Target Card satisfies the user's question. 
    2. "yn": Must be strictly "Yes" or "No".
    3. "matching": List all card codes from Current Candidates that satisfy the user's question (e.g. all face cards and cards rank < 3).
    4. "rem": Short Sarcastic remark. DO NOT any features of the Target Card here.
    5. "q": Score question quality from 0 to 100 (100 = 50/50 split).

    JSON Output Requirements (Mandatory):
    {{
      "thought": "<string>",
      "yn": "Yes" | "No",
      "matching": ["<card code>", ...],
      "rem": "<string>"
      "q": <integer 0-100>,
    }}
    """
    # try getting AI response
    try:
        with st.spinner("Answer is being created …"):
            time.sleep(0.5)
            response = client.chat.completions.create(
                model="Qwen/Qwen3.8-27B-FP8",
                messages=[
                    {"role": "system","content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=800
            )


        if response.choices[0].message.content is None: # no message to display
            with chat_container.chat_message("assistant"):
                ai_response = st.write_stream(stream_text("Great, you broke the AI  \n Reason: " + response.choices[0].finish_reason))
            st.session_state.messages.append({"role": "assistant", "content": ai_response}) # add ai_response to chat history

        else:
            # load ai response jsonn
            ai_data = json.loads(response.choices[0].message.content)

            # output response as an asisstant chat bubble
            with chat_container.chat_message("assistant"):
                ai_response = st.write_stream(stream_text(ai_data.get("yn") + "  \n" + ai_data.get("rem")))
            st.session_state.messages.append({"role": "assistant", "content": ai_response}) # add ai_response to chat history

            if st.session_state["debug"]:
                st.write(ai_data)

            # update possible and impossile cards
            if ai_data.get("yn") == "Yes":
                # if target has property keep only the card in the list that match
                st.session_state["p_cards"] = [c for c in st.session_state["p_cards"] if c in set(ai_data.get("matching", []))]

            elif ai_data.get("yn") == "No":
                #if target doesn't have property remove all matching cards from the list
                st.session_state["p_cards"] = [c for c in st.session_state["p_cards"] if c not in set(ai_data.get("matching", []))]

            # log all data in new df
            new_data = {"Question #": st.session_state["q_idx"],
                        "User Prompt": user_prompt,
                        "AI Response": ai_data.get("yn"),
                        "Global Entropy": calculate_entropy(st.session_state["p_cards"]),
                        "Information Gain": calculate_ig(st.session_state["p_cards"]),
                        "Quality of Guess (AI)": ai_data.get("q"),
                        "Quality of Guess": information_gain * 100, # would have liked to do more calc here but julian no happy
                        "Possible Cards": st.session_state["p_cards"]}
            new_df = pd.DataFrame([new_data])

            # concateate to corresponding game_dfs(used to just append but pandas no likey)
            st.session_state["game_dfs"][-1] = pd.concat([st.session_state["game_dfs"][-1], new_df], ignore_index=True)
            if st.session_state["debug"]:
                st.write(st.session_state["game_dfs"][-1])

            # update relevant game states for next innput 
            st.session_state["q_idx"] += 1

    except AuthenticationError:
        st.error("API was not accept. Please check it.")
