import streamlit as st
import random

# Sample audio files (replace these URLs with actual audio file URLs)
audio_sources = [
    "https://ai-scool.com/audio/mimi_intro.mp3",
    "https://ai-scool.com/audio/lily_intro.mp3",
    "https://ai-scool.com/audio/freya_intro.mp3"
]

# Initialize session state variables
if 'audio_index' not in st.session_state:
    st.session_state['audio_index'] = 0
if 'show_audio' not in st.session_state:
    st.session_state['show_audio'] = True

# Button to trigger a normal rerun
if st.button("Change Audio"):
    st.session_state['audio_index'] = (st.session_state['audio_index'] + 1) % len(audio_sources)
    st.session_state['show_audio'] = not st.session_state['show_audio']

# Method 1: Simple if condition
if st.session_state['show_audio']:
    st.audio(audio_sources[st.session_state['audio_index']], format='audio/mp3', autoplay=True)

# Method 2: Inside a container
with st.container():
    if st.session_state['show_audio']:
        st.audio(audio_sources[st.session_state['audio_index']], format='audio/mp3', autoplay=True)

# Method 3: Column layout
col1, col2 = st.columns(2)
with col1:
    if st.session_state['show_audio']:
        st.audio(audio_sources[st.session_state['audio_index']], format='audio/mp3', autoplay=True)

# Method 4: Expander
with st.expander("Audio Expander"):
    if st.session_state['show_audio']:
        st.audio(audio_sources[st.session_state['audio_index']], format='audio/mp3', autoplay=True)

# Method 5: Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
with tab1:
    st.write("This is tab 1.")
with tab2:
    if st.session_state['show_audio']:
        st.audio(audio_sources[st.session_state['audio_index']], format='audio/mp3', autoplay=True)
