import streamlit as st

## Button test with nesting and session state trials

st.write("Session state and button testing")

# Initialize session state
if 'count' not in st.session_state:
    st.session_state['count'] = 0
    
st.write(f"First display of count1: {st.session_state['count']}")



# Variation 1: Single Button Update
st.write("### Variation 1: Single Button Update")
single_button = st.button('Press Me - Single Update', key='a_button1')
if single_button:
    st.session_state['count'] += 1
st.write(f"Session state after single update: {st.session_state['count']}")


#placeholder placed  before the button that triggers it 2v2
count_placeholder = st.empty()



# Variation 2: Nested Button Update
st.write("### Variation 2: Nested Button Update")
nested_button_outer = st.button('Press Me - Nested Update (Outer)', key='nouter1')
if nested_button_outer:
    nested_button_inner = st.button('Press Me - Nested Update (Inner)', key='ninner1')
    if nested_button_inner:
        st.session_state['count'] += 1
st.write(f"Session state after nested update: {st.session_state['count']}")

# Define functions for further variations
def update_count():
    st.session_state['count'] += 1
    st.write(f"Session state inside function: {st.session_state['count']}")

def nested_function():
    update_count()
    st.write(f"Session state inside nested function: {st.session_state['count']}")



# Variation 2v2: Nested Button Update
st.write("### Variation 2v2: Nested Button Update numbers")
nested_button_outer = st.button('Press Me - Nested Update (Outer)', key='outer_button')
if nested_button_outer:
    st.session_state['outer_clicked'] = True

if 'outer_clicked' in st.session_state and st.session_state['outer_clicked']:
    nested_button_inner = st.button('Press Me - Nested Update (Inner)', key='inner_button')
    if nested_button_inner:
        st.session_state['count'] += 1
        st.session_state['inner_clicked'] = True

if 'inner_clicked' in st.session_state and st.session_state['inner_clicked']:
    st.session_state['outer_clicked'] = True

# Update the placeholder with the current count
count_placeholder.write(f"First display of count2: {st.session_state['count']}")
### end

## start

# Initialize the count in the session state
if 'count' not in st.session_state:
    st.session_state['count'] = 0

# Callback function to increment the count
def increment_count():
    st.session_state['count'] += 1

# Variation 2: Single Button Update
st.write("### Variation 2v2 alt: update number with on click event")
single_button = st.button('Press Me - Single Update', on_click=increment_count, key='a_button2')
st.write(f"Session state after single update: {st.session_state['count']}")

# Variation 2v2: Nested Button Update numbers
st.write("### Variation 2v2: Nested Button Update numbers")
nested_button_outer = st.button('Press Me - Nested Update (Outer)', 
                                on_click=increment_count, 
                                key='outer_button2v2n')

nested_button_inner = st.button('Press Me - Nested Update (Inner)', 
                                on_click=increment_count, 
                                key='inner_button2v2n')

# Display the current count
st.write(f"Current count: {st.session_state['count']}")


##end


#start
# Variation 2v3: Nested Button Update with Label Change
st.write("### Variation 2v3: Nested Button Update with Label Change")

# Define the labels
labels = ["cool", "green", "fun"]

# Initialize the label index in the session state
if 'label_index' not in st.session_state:
    st.session_state['label_index'] = 0

# Callback function to increment the label index
def on_click_updater():
    st.session_state['label_index'] = (st.session_state['label_index'] + 1) % len(labels)

# Create buttons with on_click parameter
nested_button_outer = st.button(labels[st.session_state['label_index']], 
                                on_click=on_click_updater, 
                                key='outer_button_v2v3')

nested_button_inner = st.button('Press Me - Nested Update (Inner)', 
                                on_click=on_click_updater, 
                                key='inner_button_v2v3')

additional_button = st.button('Additional Button', 
                              on_click=on_click_updater, 
                              key='additional_button')

# Display the current label
st.write(f"Current label: {labels[st.session_state['label_index']]}")

### end


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
