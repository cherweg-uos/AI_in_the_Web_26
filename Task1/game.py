import streamlit as st
import pandas as pd
from st_clickable_images import clickable_images
from openai import OpenAI, AuthenticationError, OpenAIError
import random
import math
import base64
import json 
import time
import os 



# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key= st.session_state["AI_KEY"]
)

st.title("Guessing Game", text_alignment="center")

st.set_page_config(layout="wide")

# function to call when resetting the game
def game_reset() -> None:
    st.session_state["number"] = random.randint(0,51) # remove selected cart
    st.info("New Card Selected!")
    del st.session_state["last_guess"] # remove last guess
    st.session_state["q_idx"] = 0 # reset question index
    st.session_state["g_idx"] += 1 # increase the game index
    st.session_state["game_dfs"].append(pd.DataFrame(columns=st.session_state["columns"])) # add new game df to game_dfs

def calculate_entropy(p_cards, i_cards) -> tuple[float, float]:
    p_hit = 1/len(p_cards)
    if p_hit == 1:
        return 0, 0
    p_miss = 1 - p_hit
    local_entropy = -(p_hit * math.log2(p_hit) + p_miss * math.log2(p_miss))
    global_entropy = (len(p_cards) / (len(p_cards) + len(i_cards)) * local_entropy)
    return local_entropy, global_entropy

# create a new random number if we don't have one yet / und ein knopf wird erstelt 
resetbuton = st.button("Restart the Game", width="stretch")
if resetbuton:
    game_reset()

#falls noch keine nummer festgelegt ist wird hier random eine zwischen 0 and 51
if ("number" not in st.session_state) or resetbuton:
    st.session_state["number"] = random.randint(0,51)
    
# debug info for selected card
if st.session_state["debug"]:
    st.text(f"The number is #{st.session_state['number']}, which is \"{st.session_state["cards_names"][st.session_state["number"]]}\"")
    st.image(st.session_state["cards_paths"][st.session_state["number"]], width=250) #dateipfadliste[zufallsnummer]

st.divider()

st.subheader("Ask a LLM for hints")
prompt = st.text_area("Question to ask: (Responses will be Yes/No only)")
#abrufen von base64 image 
base64_image = st.session_state["cards_base64"][st.session_state["number"]]
if st.button("Submit", disabled=not prompt.strip(), shortcut="Enter"):
    try:
        with st.spinner("Answer is being created …"):
            time.sleep(1)
            response = client.chat.completions.create(
                model="google/gemma-4-E4B-it",
                messages=[{"role": "developer", "content": f"""
                You are the game master for a card-guessing game using a standard French 52-card deck.
                The user is trying to guess the hidden target card by asking yes/no questions.

                ### Game State
                - Target Card: {st.session_state["cards_names"][st.session_state["number"]]}
                - Question Number: {st.session_state["q_idx"]}
                - Remaining Possible Cards [p_cards]: {st.session_state["p_cards"]}

                ### Evaluation Rules
                1. Determine whether the user's question is a valid Yes/No question about properties of the target card.
                2. If the question cannot be answered with Yes/No or is ambiguous:
                - Set "yn_response" to null.
                - Set "eliminated_cards" to [].
                - Set "quality" to 0.
                - Explain the issue in "remark".
                3. If the question is valid:
                - Answer strictly against the Target Card ("Yes" or "No" in the language of the question).
                - Identify every card in [p_cards] that contradicts the answer and return them in "eliminated_cards".
                - Do NOT return the full deck or uneliminated cards.
                4. Estimate Question Quality (integer from 0 to 100) based on strategic expected information gain, NOT the actual outcome:
                - 90~100: Near-optimal binary split (divides [p_cards] roughly 50/50 regardless of the answer).
                - 60~89: Useful broader partition (e.g., suit, rank range).
                - 10~59: Highly unbalanced/risky question (e.g., guessing a single card when many candidates remain).
                - 0: Tautological, redundant (eliminates 0 cards under either outcome), or invalid question.

                ### Output Format
                Always return a valid JSON object matching this schema:
                {{
                "yn_response": "Yes" | "No" | null,
                "eliminated_cards": ["<card_name>", ...],
                "quality": <integer 0-100>,
                "remark": "<sarcastic comment, or explanation if question was invalid/ambiguous>"
                }}
                """},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": base64_image}}],},
                    {"role": "user", "content": prompt}
                   ],
                response_format={"type": "json_object"})

        # load ai response jsonn
        ai_data = json.loads(response.choices[0].message.content)

        # show responses in browser
        if st.session_state["debug"]:
            st.write(ai_data)
        st.write(ai_data.get("remark"))
        st.write(ai_data.get("yn_response"))

        # update possible and impossile cards
        eliminated = set(ai_data.get("eliminated_cards", [])) #
        st.session_state["p_cards"] = [c for c in st.session_state["p_cards"] if c not in eliminated] # add only non eliminated cards back
        st.session_state["i_cards"].extend(eliminated) # add new excluded cards

        # calculate entropy and information gain
        local_entropy, global_entropy = calculate_entropy(st.session_state["p_cards"], st.session_state["i_cards"])
        information_gain = st.session_state["game_dfs"][-1]["Global Entropy"][-1] - global_entropy

        # log all data in new df
        new_data = {"Question #": st.session_state["q_idx"],
                    "User Prompt": prompt,
                    "AI Response": ai_data.get("yn_response"),
                    "Possible Cards": st.session_state["p_cards"],
                    "Impossible Cards": st.session_state["i_cards"],
                    "Global Entropy": global_entropy,
                    "Information Gain": information_gain,
                    "Quality of Guess": ai_data.get("quality")}
        new_df = pd.DataFrame([new_data])
        if st.session_state["debug"]:
            st.write(new_df)

        # concateate to corresponding game_dfs(used to just append but pandas no likey)
        st.session_state["game_dfs"][st.session_state["g_idx"]] = pd.concat([st.session_state["game_dfs"][st.session_state["g_idx"]], new_df], ignore_index=True)
        if st.session_state["debug"]:
            st.write(st.session_state["game_dfs"][st.session_state["g_idx"]])

        # update relevant game states for next innput 
        st.session_state["q_idx"] += 1

    except AuthenticationError:
        st.error("API was not accept. Please check it.")

st.divider()

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

# Submit buton displaying selected card
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
        st.session_state["results"].append(1)
    else:
        st.error("Oh no. The Card is wrong.")
        st.session_state["results"].append(0)
    time.sleep(500) # wait a bit before forced reset
    game_reset() #forced reset so you can't add guesses once the game is over
        
