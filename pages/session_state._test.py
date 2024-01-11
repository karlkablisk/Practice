import streamlit as st

## Button test with nesting and session state trials

st.write("Session state and button testing")

# Initialize session state
if 'count' not in st.session_state:
    st.session_state['count'] = 0
    
st.write(f"First display of count: {st.session_state['count']}")



# Variation 1: Single Button Update
st.write("### Variation 1: Single Button Update")
single_button = st.button('Press Me - Single Update', key='a_button1')
if single_button:
    st.session_state['count'] += 1
st.write(f"Session state after single update: {st.session_state['count']}")


#placeholder placed  before the button that triggers it
count_placeholder = st.empty()


# Variation 2: Nested Button Update
st.write("### Variation 2: Nested Button Update")
nested_button_outer = st.button('Press Me - Nested Update (Outer)', key='outer_button')
if nested_button_outer:
    nested_button_inner = st.button('Press Me - Nested Update (Inner)', key='inner_button')
    if nested_button_inner:
        st.session_state['count'] += 1
st.write(f"Session state after nested update: {st.session_state['count']}")

# Variation 2v2: Nested Button Update
st.write("### Variation 2v2: Nested Button Update numbers")
nested_button_outer = st.button('Press Me - Nested Update (Outer)', key='outer_button2')
if nested_button_outer:
    st.session_state['outer_clicked'] = True

if 'outer_clicked' in st.session_state and st.session_state['outer_clicked']:
    nested_button_inner = st.button('Press Me - Nested Update (Inner)', key='inner_button2')
    if nested_button_inner:
        st.session_state['count'] += 1
        st.session_state['inner_clicked'] = True

if 'inner_clicked' in st.session_state and st.session_state['inner_clicked']:
    st.session_state['outer_clicked'] = True

# Variation 2v2 alt: update number with on click event
st.write("### Variation 2v2 alt: update number with on click event")
single_button = st.button('Press Me - Single Update', on_click=increment_count, key='single_button')
st.write(f"Session state after single update: {st.session_state['count']}")

# Variation 2v3: Nested Button Update with Label Change
st.write("### Variation 2v3: Nested Button Update with Label Change")
nested_button_outer = st.button(labels[st.session_state['label_index']], 
                                on_click=on_click_updater, 
                                key='outer_button3')

nested_button_inner = st.button('Press Me - Nested Update (Inner)', 
                                on_click=on_click_updater, 
                                key='inner_button3')

additional_button = st.button('Additional Button', 
                              on_click=on_click_updater, 
                              key='additional_button')

# Variation 3: Function Update
st.write("### Variation 3: Function Update")
function_button = st.button('Press Me - Function Update', key='function_button')
if function_button:
    update_count()

# Variation 4: Nested Function Update
st.write("### Variation 4: Nested Function Update")
nested_function_button = st.button('Press Me - Nested Function Update', key='nested_function_button')
if nested_function_button:
    nested_function()

# Variation 5: Button in Function Update
st.write("### Variation 5: Button in Function Update")
inner_button = st.button('Press Inner Button - Function Update', key='inner_button4')
if inner_button:
    st.session_state['count'] += 1
    st.write(f"Session state after button in function: {st.session_state['count']}")

# Variation 6: Function in Button Update
st.write("### Variation 6: Function in Button Update")
function_in_button = st.button('Press Me - Function in Button Update', key='function_in_button')
if function_in_button:
    update_count()

# Variation 7: Multiple Buttons Update
st.write("### Variation 7: Multiple Buttons Update")
multi_button1 = st.button('Press Me - Multiple Update 1', key='multi_button1')
if multi_button1:
    st.session_state['count'] += 1
multi_button2 = st.button('Press Me - Multiple Update 2', key='multi_button2')
if multi_button2:
    st.session_state['count'] += 1
st.write(f"Session state after multiple updates: {st.session_state['count']}")

# Variation 8: Button with Function Call Update
st.write("### Variation 8: Button with Function Call Update")
button_function_call = st.button('Press Me - Button with Function Call', key='button_function_call')
if button_function_call:
    update_count()

# Variation 9: Complex Nested Update
st.write("### Variation 9: Complex Nested Update")
complex_button1 = st.button('Press Me - Complex Nested Update 1', key='complex_button1')
if complex_button1:
    complex_button2 = st.button('Press Me - Complex Nested Update 2', key='complex_button2')
    if complex_button2:
        update_count()
        complex_function_button = st.button('Press Me - Complex Nested Function', key='complex_function_button')
        if complex_function_button:
            nested_function()

st.write("Final session state:", st.session_state['count'])
