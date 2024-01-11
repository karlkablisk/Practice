import streamlit as st
import requests
import base64

# URLs of your audio files
audio_sources = [
    "https://ai-scool.com/audio/mimi_intro.mp3",
    "https://ai-scool.com/audio/lily_intro.mp3",
    "https://ai-scool.com/audio/freya_intro.mp3"
]

# Function to fetch and encode audio data to base64
def fetch_and_encode_audio(url):
    response = requests.get(url)
    audio_data = response.content
    return base64.b64encode(audio_data).decode('utf-8')  

# Fetch and encode audio
audio_base64 = fetch_and_encode_audio(audio_sources[st.session_state['audio_index']])

# Define the audio HTML element
#audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""

# Initialize session state variables
if 'audio_index' not in st.session_state:
    st.session_state['audio_index'] = 0
if 'play_audio' not in st.session_state:
    st.session_state['play_audio'] = False

# Button to trigger a normal rerun 
if st.button("Change Audio"):
    st.session_state['audio_index'] = (st.session_state['audio_index'] + 1) % len(audio_sources)
    st.session_state['play_audio'] = True

# Unrelated button to trigger a rerun
if st.button("Click me for unrelated action"):
    st.write("Unrelated action triggered")

# Define the audio HTML element
if st.session_state['play_audio']:
    audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state['play_audio'] = False

    # Define the audio HTML element
if st.session_state['play_audio'] and st.session_state['counter'] % 3 == 0:
    audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state['play_audio'] = False


# Method 8
st.write("Method 8: Displaying the audio based on a counter in session state")
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0
st.session_state['counter'] += 1
if st.session_state['counter'] % 3 == 0:
    audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
   
    st.markdown(audio_html, unsafe_allow_html=True)
