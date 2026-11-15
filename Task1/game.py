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


# function to call when resetting the game
def game_reset() -> None:
    st.session_state["number"] = random.randint(0,51) # remove selected cart
    st.session_state["last_guess"] = None # remove last guess
    st.session_state["q_idx"] = 0 # reset question index
    st.session_state["g_idx"] += 1 # increase the game index
    st.session_state["game_dfs"].append(pd.DataFrame([{"Question #": 0,
                                                        "User Prompt": "",
                                                        "AI Response": "",
                                                        "Possible Cards": st.session_state["p_cards"],
                                                        "Impossible Cards": st.session_state["i_cards"],
                                                        "Global Entropy": calculate_entropy(st.session_state["p_cards"], [])[1],
                                                        "Information Gain": "",
                                                        "Quality of Guess (AI)": "",
                                                        "Quality of Guess": ""}])) # add new game df to game_dfs
    st.session_state["reset"] = True
    st.rerun()
    

def calculate_entropy(p_cards, i_cards) -> tuple[float, float]:
    p_hit = 1/len(p_cards)
    if p_hit == 1:
        return 0, 0
    p_miss = 1 - p_hit
    local_entropy = -(p_hit * math.log2(p_hit) + p_miss * math.log2(p_miss))
    global_entropy = (len(p_cards) / (len(p_cards) + len(i_cards)) * local_entropy)
    return local_entropy, global_entropy

if st.session_state["reset"]:
    st.info("Game has been Reset")
    st.session_state["reset"] = False

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
    st.text(f"The number is #{st.session_state['number']}, which is \"{st.session_state["cards_names"][st.session_state["number"]]}\"")
    st.image(st.session_state["cards_paths"][st.session_state["number"]], width=250) #dateipfadliste[zufallsnummer]

st.divider()

st.subheader("Ask a LLM for hints")
user_prompt = st.text_area("Question to ask: (Responses will be Yes/No only)")
#abrufen von base64 image 
base64_image = st.session_state["cards_base64"][st.session_state["number"]]
if st.button("Submit", disabled=not user_prompt.strip(), shortcut="Enter"):
    # generate new system promt
    system_prompt = f"""
    You are a strict, infallible referee for a 52-card guessing game.
    Target Card in Image: {st.session_state["cards_names"][st.session_state["number"]]} ({st.session_state["short_cards_names"][st.session_state["number"]]})
    Current Remaining Candidates: {st.session_state["p_cards"]}

    Rules:
    1. "thought": In exactly 1 short sentence briefly analyze if the Target Card satisfies the user's question. 
    2. "yn": Must be strictly "Yes" or "No".
    3. "elim": A Python-style list of card names from the "Current Remaining Candidates" that must be ELIMINATED based on the user's question and your "yn" answer. 
       - If yn is "Yes": eliminate all remaining candidates that DO NOT match the question.
       - If yn is "No": eliminate all remaining candidates that DO match the question.
       - CRITICAL: The Target Card must NEVER be in "elim".
    4. "q": Score question quality from 0 to 100 (100 = 50/50 split).
    5. "rem": Short Sarcastic remark.

    JSON Output Requirements (Mandatory):
    {{
      "thought": "<string>",
      "yn": "Yes" | "No",
      "elim": ["<Card Name>", ...],
      "q": <integer 0-100>,
      "rem": "<string>"
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

        # load ai response jsonn
        ai_data = json.loads(response.choices[0].message.content)

        # show responses in browser
        if st.session_state["debug"]:
            st.write(ai_data)
        st.write(ai_data.get("rem"))
        st.write(ai_data.get("yn"))

        # update possible and impossile cards
        eliminated = set(ai_data.get("elim", []))
        st.session_state["p_cards"] = [c for c in st.session_state["p_cards"] if c not in eliminated] # add only non eliminated cards back
        st.session_state["i_cards"].extend(eliminated) # add new excluded cards

        # calculate entropy and information gain
        _, global_entropy = calculate_entropy(st.session_state["p_cards"], st.session_state["i_cards"])
        information_gain = st.session_state["game_dfs"][-1]["Global Entropy"].iloc[-1] - global_entropy

        # log all data in new df
        new_data = {"Question #": st.session_state["q_idx"],
                    "User Prompt": user_prompt,
                    "AI Response": ai_data.get("yn"),
                    "Possible Cards": st.session_state["p_cards"],
                    "Impossible Cards": st.session_state["i_cards"],
                    "Global Entropy": global_entropy,
                    "Information Gain": information_gain,
                    "Quality of Guess (AI)": ai_data.get("q"),
                    "Quality of Guess": ""}
        new_df = pd.DataFrame([new_data])
        if st.session_state["debug"]:
            st.write(new_df)

        # concateate to corresponding game_dfs(used to just append but pandas no likey)
        st.session_state["game_dfs"][-1] = pd.concat([st.session_state["game_dfs"][-1], new_df], ignore_index=True)
        if st.session_state["debug"]:
            st.write(st.session_state["game_dfs"][-1])

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
        st.session_state["results"].append(-1)
    with st.spinner("Game is being reset …"):
        time.sleep(2) # wait a bit before forced reset
        game_reset() #forced reset so you can't add guesses once the game is over
        
