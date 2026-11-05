import streamlit as st
import random

#Tab name 
st.header("Guessing Game")

# create list of all cards using unicode characters/ wir verwenden keine mehr right? 
deck = []
for hex in range(0x0001F0A1,0x0001F0DF):
    if (hex % 16) not in [0, 12, 15]: # who TF put mahjong tiles between the playing cards?
        deck.append(chr(hex))


# create a new random number if we don't have one yet / und ein knopf wird erstelt 
resetbuton = st.button("Reset", width="stretch", shortcut="Space")

#falls noch keine nummer festgelegt ist wird hier random eine zwischen 0&51
if ("number" not in st.session_state) or resetbuton:
    st.session_state["number"] = random.randint(0,51)
    st.info("New Card Selected!")

#Wenn session state auf debug ist dann    
if st.session_state["debug"]:
    st.text(f"The number is {st.session_state['number']}") # wird text angezeigt mit dem session state number 
    st.image({"cards/" + st.session_state["SVGList"][st.session_state["number"]]}) #hmmm, hier wird glaube ich irgendwie das image angezeigt das verstehe ich noch nicht ganz 

with st.form("number_form"): # du musst mir nochmal with erklären 
    guess = st.text_input("Enter Question or a Guess")
    submitted = st.form_submit_button("Submit") #button subbmit 

if submitted:
    st.write(f"You submitted: {guess}") # submitet gues wird nochmal angezeigt
    # Run your calculation or other action here.
    if guess == st.session_state['number']:
        st.success("Yeah! You did it")
        del st.session_state['number']
    else:
        st.error("Oh no. The Card is wrong.")
        st.write(st.session_state['number'])

####das ist eine andere version 