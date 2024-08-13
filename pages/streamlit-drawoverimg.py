import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pandas as pd

# Sidebar for drawing tool selection and settings
st.sidebar.header("Settings")

# Load an image file
bg_image = st.sidebar.file_uploader("Upload a background image:", type=["png", "jpg"])

# Select drawing tool
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("rect", "freedraw", "line", "circle", "transform")
)

# Stroke width and color settings
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ", "#000000")
bg_color = st.sidebar.color_picker("Background color hex: ", "#ffffff")

# Option to update canvas in real-time
realtime_update = st.sidebar.checkbox("Update in realtime", True)

# Create the drawable canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=Image.open(bg_image) if bg_image else None,
    update_streamlit=realtime_update,
    height=400,
    width=600,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Display the drawn image
if canvas_result.image_data is not None:
    st.image(canvas_result.image_data)

# Display JSON data of drawn objects
if canvas_result.json_data is not None:
    objects = pd.json_normalize(canvas_result.json_data["objects"]) 
    for col in objects.select_dtypes(include=['object']).columns:
        objects[col] = objects[col].astype("str")
    st.dataframe(objects)
