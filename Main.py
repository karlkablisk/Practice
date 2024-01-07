import streamlit as st

if 'count' not in st.session_state:
    st.session_state['count'] = 0

button = st.button('press me')

if button:
    st.session_state['count'] += 1

st.write(st.session_state)
