import streamlit as st
import random

st.header("Guessing Game")

# create list of all cards using unicode characters
deck = []
for hex in range(0x0001F0A1,0x0001F0DF):
    if (hex % 16) not in [0, 12, 15]: # who TF put mahjong tiles between the playing cards?
        deck.append(chr(hex))


# create a new random number if we don't have one yet
resetbuton = st.button("Reset", width="stretch", shortcut="Space")

if ("number" not in st.session_state) or resetbuton:
    st.session_state["number"] = random.randint(0,51)
    st.info("New Card Selected!")
    
if st.session_state["debug"]:
    st.text(f"The number is {st.session_state['number']}")
    st.image({"cards/" + st.session_state["SVGList"][st.session_state["number"]]})

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

