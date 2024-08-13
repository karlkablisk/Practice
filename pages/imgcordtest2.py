import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

# Function to draw a rectangle on the image
def draw_rectangle(img, coords):
    draw = ImageDraw.Draw(img)
    draw.rectangle(coords, outline="red", width=2)
    return img

# Function to display coordinates on Streamlit
def display_coordinates():
    st.write(f"Coordinates: {st.session_state['coords']}")

st.title("Click on the image to get coordinates")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    img_array = np.array(img)

    # Set up sliders to simulate click coordinates
    st.write("Use the sliders to select a point on the image.")
    x = st.slider("X coordinate", 0, img.width, 0)
    y = st.slider("Y coordinate", 0, img.height, 0)

    # Save the coordinates in the session state
    if st.button("Save Coordinates"):
        st.session_state['coords'] = (x, y)
        st.session_state['rect'] = [x - 10, y - 10, x + 10, y + 10]

    # Draw a rectangle around the selected point
    if 'rect' in st.session_state:
        img_with_rect = draw_rectangle(img.copy(), st.session_state['rect'])
        st.image(img_with_rect, use_column_width=True)

    # Display the coordinates
    if 'coords' in st.session_state:
        display_coordinates()
else:
    st.write("Please upload an image file to proceed.")
