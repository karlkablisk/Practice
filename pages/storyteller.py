import os
import streamlit as st
from openai import OpenAI
  
# Initialize the OpenAI client with the API key from the environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set a default model
model = "gpt-4o-mini"

st.title("Interactive RPG Storytelling with GPT-4o-mini")

# Step 1: Character Creation
if "character_created" not in st.session_state:
    st.session_state.character_created = False

if not st.session_state.character_created:
    st.header("Create Your Character")
    
    character_name = st.text_input("Enter your character's name:")
    character_class = st.selectbox("Choose your class:", ["Warrior", "Mage", "Rogue", "Bard"])
    character_race = st.selectbox("Choose your race:", ["Human", "Elf", "Dwarf", "Orc"])
    character_level = st.slider("Choose your level:", 1, 20, 1)
    character_background = st.text_area("Describe your character's background:")

    if st.button("Start Adventure"):
        if character_name and character_class and character_race:
            st.session_state.character_created = True
            st.session_state.character = {
                "name": character_name,
                "class": character_class,
                "race": character_race,
                "level": character_level,
                "background": character_background
            }
        else:
            st.error("Please complete all character fields to start your adventure.")
else:
    # Character Summary
    st.sidebar.header("Your Character")
    st.sidebar.write(f"**Name:** {st.session_state.character['name']}")
    st.sidebar.write(f"**Class:** {st.session_state.character['class']}")
    st.sidebar.write(f"**Race:** {st.session_state.character['race']}")
    st.sidebar.write(f"**Level:** {st.session_state.character['level']}")
    st.sidebar.write(f"**Background:** {st.session_state.character['background']}")

    # Story container
    st.write(f"**Welcome, {st.session_state.character['name']} the {st.session_state.character['class']} of {st.session_state.character['race']} race, Level {st.session_state.character['level']}**")
    
    # Initialize story history
    if "story" not in st.session_state:
        st.session_state.story = [
            {"role": "system", "content": f"You are {st.session_state.character['name']}, a {st.session_state.character['class']} from the {st.session_state.character['race']} race. Your journey begins now."}
        ]

    # Display story messages
    for message in st.session_state.story:
        with st.container():
            st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")

    # Input columns for user actions
    col1, col2 = st.columns(2)

    with col1:
        user_action = st.text_input("What will you do?", "")

    with col2:
        st.write("")

    if st.button("Take Action"):
        if user_action:
            # Add user action to the story
            st.session_state.story.append({"role": "user", "content": user_action})
            
            # Display user's action
            with st.container():
                st.markdown(f"**You:** {user_action}")
            
            # Generate story continuation using GPT-4o-mini
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": f"You are a {st.session_state.character['class']} named {st.session_state.character['name']} from the {st.session_state.character['race']} race."},
                        *st.session_state.story
                    ],
                    max_tokens=200
                ).choices[0].message.content
                
                # Display AI response in the story
                with st.container():
                    st.markdown(f"**Narrator:** {response}")
                
                # Add response to the story history
                st.session_state.story.append({"role": "assistant", "content": response})
            
            except Exception as e:
                st.error(f"Error generating response: {e}")

    # End the adventure or continue
    if st.button("End Adventure"):
        st.write("**Your adventure has come to an end. Thank you for playing!**")
        st.session_state.story.clear()
        st.session_state.character_created = False
