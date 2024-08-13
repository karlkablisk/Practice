import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pandas as pd

# Sidebar for drawing tool selection and settings
st.sidebar.header("Settings")

# Upload an image file
uploaded_image = st.file_uploader("Upload an image to draw on:", type=["png", "jpg", "jpeg"])

if uploaded_image:
    # Open the uploaded image
    image = Image.open(uploaded_image)

    # Select drawing tool
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("rect", "freedraw", "line", "circle", "transform")
    )

    # Stroke width and color settings
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ", "#000000")

    # Option to update canvas in real-time
    realtime_update = st.sidebar.checkbox("Update in realtime", True)

    # Create the drawable canvas directly over the uploaded image
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=image,  # Directly set the uploaded image as background
        update_streamlit=realtime_update,
        height=image.height,
        width=image.width,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    # Display the final image with drawings
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)

    # Display JSON data of drawn objects
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"]) 
        for col in objects.select_dtypes(include=['object']).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)
else:
    st.write("Please upload an image to begin drawing.")
