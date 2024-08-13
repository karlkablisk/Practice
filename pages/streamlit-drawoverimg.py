import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pandas as pd

def main():
    st.title("Image Annotation Tool")
    st.sidebar.header("Configuration")

    # Upload an image file
    bg_image = st.sidebar.file_uploader("Upload an image:", type=["png", "jpg", "jpeg"])

    # Check if an image is uploaded
    if bg_image is not None:
        image = Image.open(bg_image)

        # Drawing settings
        stroke_width = st.sidebar.slider("Stroke width:", 1, 25, 3)
        stroke_color = st.sidebar.color_picker("Stroke color:", "#ff0000")
        bg_color = st.sidebar.color_picker("Background color:", "#ffffff")

        # Real-time update checkbox
        realtime_update = st.sidebar.checkbox("Update in realtime", True)

        # Create the drawable canvas with the image as the background
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Optional fill color for drawn shapes
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            background_image=image,  # Set the uploaded image as the background
            update_streamlit=realtime_update,
            height=image.height,
            width=image.width,
            drawing_mode="rect",  # Set to 'rect' for rectangle drawing
            key="canvas",
        )

        # Display the drawn image if available
        if canvas_result.image_data is not None:
            st.image(canvas_result.image_data)

        # Display JSON data of drawn objects if available
        if canvas_result.json_data is not None:
            objects = pd.json_normalize(canvas_result.json_data["objects"])
            for col in objects.select_dtypes(include=['object']).columns:
                objects[col] = objects[col].astype("str")
            st.dataframe(objects)
    else:
        st.warning("Please upload an image to start drawing.")

if __name__ == "__main__":
    st.set_page_config(page_title="Drawable Canvas Demo", page_icon=":pencil:")
    main()
