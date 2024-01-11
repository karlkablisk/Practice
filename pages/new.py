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

# Methods for conditional rendering of audio element

# Method 1: Using Session State Toggle
if st.session_state['show_audio']:
    st.markdown(audio_html, unsafe_allow_html=True)
st.session_state['show_audio'] = not st.session_state['show_audio']

# Method 2: Rendering Inside a Text Element
if st.session_state['show_audio']:
    st.text('Audio below:')
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 3: Using a Checkbox to Control Display
if st.checkbox("Show Audio", value=st.session_state['show_audio']):
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 4: Conditional Rendering Inside a Function
def render_audio():
    if st.session_state['show_audio']:
        st.markdown(audio_html, unsafe_allow_html=True)
render_audio()

# Method 5: Using a Placeholder
placeholder = st.empty()
if st.session_state['show_audio']:
    placeholder.markdown(audio_html, unsafe_allow_html=True)

# Method 6: Using a Custom Button to Control Audio
if st.button("Toggle Audio"):
    st.session_state['show_audio'] = not st.session_state['show_audio']
if st.session_state['show_audio']:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 7: Rendering Audio in a Sidebar
if st.session_state['show_audio']:
    with st.sidebar:
        st.markdown(audio_html, unsafe_allow_html=True)

# Method 8: Conditional Rendering with a Slider
if st.slider("Volume", 0, 100, 50) > 50:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 9: Using Session State with Key-Value Pair
if 'audio_rendered' not in st.session_state:
    st.session_state['audio_rendered'] = st.session_state['show_audio']
if st.session_state['audio_rendered']:
    st.markdown(audio_html, unsafe_allow_html=True)
    st.session_state['audio_rendered'] = False

# Method 10: Rendering Inside a Custom Function with Argument
def render_audio_conditional(show):
    if show:
        st.markdown(audio_html, unsafe_allow_html=True)
render_audio_conditional(st.session_state['show_audio'])

