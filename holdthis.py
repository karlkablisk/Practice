

# Unrelated button to trigger a rerun
if st.button("Click me for unrelated action"):
    st.write("Unrelated action triggered")
    
# Method 1
st.write("Method 1: Using an empty container")
audio_container = st.empty()
audio_container.markdown(audio_html, unsafe_allow_html=True)
audio_container.empty()

# Method 2
st.write("Method 2: Randomly displaying the audio")
import random
if random.randint(0, 1) == 0:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 3
st.write("Method 3: Delayed display of the audio")
import time
time.sleep(1)
st.markdown(audio_html, unsafe_allow_html=True)

# Method 4
st.write("Method 4: Displaying the audio based on the current minute")
import datetime
if datetime.datetime.now().minute % 2 == 0:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 5
st.write("Method 5: Displaying the audio based on user input length")
user_input = st.text_input("Enter some text")
if len(user_input) > 5:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 6
st.write("Method 6: Displaying the audio in an expander")
with st.expander("Expand for audio"):
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 7
st.write("Method 7: Displaying the audio in the sidebar")
with st.sidebar:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 8
st.write("Method 8: Displaying the audio based on a counter in session state")
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0
st.session_state['counter'] += 1
if st.session_state['counter'] % 3 == 0:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 9
st.write("Method 9: Toggling the audio display with session state")
if 'toggle_audio' not in st.session_state:
    st.session_state['toggle_audio'] = False
if st.session_state['toggle_audio']:
    st.markdown(audio_html, unsafe_allow_html=True)

# Method 10
st.write("Method 10: Displaying the audio based on a flag in session state")
if 'audio_rendered' not in st.session_state:
    st.session_state['audio_rendered'] = False
if st.session_state['audio_rendered']:
    st.markdown(audio_html, unsafe_allow_html=True)
    
# Method 6v2: Using a Custom Button to Control Audio
st.write("Method 6v2: Using a Custom Button to Control Audio")
if st.button("Toggle Audio"):
    st.session_state['show_audio'] = not st.session_state['show_audio']
if st.session_state['show_audio']:
    st.markdown(audio_html, unsafe_allow_html=True)