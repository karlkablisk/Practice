import streamlit as st

# Initialize session state
if 'count' not in st.session_state:
    st.session_state['count'] = 0

# Variation 1: Single Button Update
st.write("### Variation 1: Single Button Update")
single_button = st.button('Press Me - Single Update')
if single_button:
    st.session_state['count'] += 1
st.write(f"Session state after single update: {st.session_state['count']}")

# Variation 2: Nested Button Update
st.write("### Variation 2: Nested Button Update")
nested_button_outer = st.button('Press Me - Nested Update (Outer)')
if nested_button_outer:
    nested_button_inner = st.button('Press Me - Nested Update (Inner)')
    if nested_button_inner:
        st.session_state['count'] += 1
st.write(f"Session state after nested update: {st.session_state['count']}")

# Variation 2v2: Nested Button Update
st.write("### Variation 2v2: Nested Button Update")
nested_button_outer = st.button('Press Me - Nested Update (Outer)')
if nested_button_outer:
    st.session_state['outer_clicked'] = True

if 'outer_clicked' in st.session_state and st.session_state['outer_clicked']:
    nested_button_inner = st.button('Press Me - Nested Update (Inner)')
    if nested_button_inner:
        st.session_state['count'] += 1
        st.session_state['outer_clicked'] = False  # Reset the state

st.write(f"Session state after nested update: {st.session_state['count']}")



# Define functions for further variations
def update_count():
    st.session_state['count'] += 1
    st.write(f"Session state inside function: {st.session_state['count']}")

def nested_function():
    update_count()
    st.write(f"Session state inside nested function: {st.session_state['count']}")

# Variation 3: Function Update
st.write("### Variation 3: Function Update")
function_button = st.button('Press Me - Function Update')
if function_button:
    update_count()

# Variation 4: Nested Function Update
st.write("### Variation 4: Nested Function Update")
nested_function_button = st.button('Press Me - Nested Function Update')
if nested_function_button:
    nested_function()

# Variation 5: Button in Function Update
st.write("### Variation 5: Button in Function Update")
def button_in_function():
    inner_button = st.button('Press Inner Button - Function Update')
    if inner_button:
        st.session_state['count'] += 1
        st.write(f"Session state after button in function: {st.session_state['count']}")
button_in_function()

# Variation 6: Function in Button Update
st.write("### Variation 6: Function in Button Update")
function_in_button = st.button('Press Me - Function in Button Update')
if function_in_button:
    update_count()

# Variation 7: Multiple Buttons Update
st.write("### Variation 7: Multiple Buttons Update")
multi_button1 = st.button('Press Me - Multiple Update 1')
if multi_button1:
    st.session_state['count'] += 1
multi_button2 = st.button('Press Me - Multiple Update 2')
if multi_button2:
    st.session_state['count'] += 1
st.write(f"Session state after multiple updates: {st.session_state['count']}")

# Variation 8: Button with Function Call Update
st.write("### Variation 8: Button with Function Call Update")
button_function_call = st.button('Press Me - Button with Function Call')
if button_function_call:
    update_count()

# Variation 9: Complex Nested Update
st.write("### Variation 9: Complex Nested Update")
complex_button1 = st.button('Press Me - Complex Nested Update 1')
if complex_button1:
    complex_button2 = st.button('Press Me - Complex Nested Update 2')
    if complex_button2:
        update_count()
        complex_function_button = st.button('Press Me - Complex Nested Function')
        if complex_function_button:
            nested_function()

st.write("Final session state:", st.session_state['count'])
