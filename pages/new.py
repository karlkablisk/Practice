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

# Initialize session state variables
if 'audio_index' not in st.session_state:
    st.session_state['audio_index'] = 0
if 'show_audio' not in st.session_state:
    st.session_state['show_audio'] = True

# Button to trigger a normal rerun
if st.button("Change Audio"):
    st.session_state['audio_index'] = (st.session_state['audio_index'] + 1) % len(audio_sources)
    st.session_state['show_audio'] = not st.session_state['show_audio']

# Fetch and encode audio
audio_base64 = fetch_and_encode_audio(audio_sources[st.session_state['audio_index']])

# Method 1: Simple if condition
if st.session_state['show_audio']:
    audio_html = f"""<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 2: Inside a container
with st.container():
    if st.session_state['show_audio']:
        st.markdown(audio_html, unsafe_allow_html=True)

# Method 3: Column layout
col1, col2 = st.columns(2)
with col1:
    if st.session_state['show_audio']:
        st.markdown(audio_html, unsafe_allow_html=True)

# Method 4: Expander
with st.expander("Audio Expander"):
    if st.session_state['show_audio']:
        st.markdown(audio_html, unsafe_allow_html=True)

# Method 5: Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
with tab1:
    st.write("This is tab 1.")
with tab2:
    if st.session_state['show_audio']:
        st.markdown(audio_html, unsafe_allow_html=True)
