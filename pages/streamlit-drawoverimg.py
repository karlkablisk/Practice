import base64
import json
import os
import re
import time
import uuid
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from svgpathtools import parse_path

def main():
    if "button_id" not in st.session_state:
        st.session_state["button_id"] = ""
    if "color_to_label" not in st.session_state:
        st.session_state["color_to_label"] = {}

    PAGES = {
        "About": about,
        "Basic example": full_app,
        "Get center coords of circles": center_circle_app,
        "Color-based image annotation": color_annotation_app,
        "Download Base64 encoded PNG": png_export,
        "Compute the length of drawn arcs": compute_arc_length,
    }
    page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    PAGES[page]()

    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://twitter.com/andfanilo">@andfanilo</a></h6>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="margin: 0.75em 0;"><a href="https://www.buymeacoffee.com/andfanilo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a></div>',
            unsafe_allow_html=True,
        )

def about():
    st.markdown(
        """
    Welcome to the demo of [Streamlit Drawable Canvas](https://github.com/andfanilo/streamlit-drawable-canvas).
    
    On this site, you will find a full use case for this Streamlit component, and answers to some frequently asked questions.
    
    :pencil: [Demo source code](https://github.com/andfanilo/streamlit-drawable-canvas-demo/)    
    """
    )
    st.image("img/demo.gif")
    st.markdown(
        """
    What you can do with Drawable Canvas:

    * Draw freely, lines, circles, and boxes on the canvas, with options on stroke & fill
    * Rotate, skew, scale, move any object on the canvas on demand
    * Select a background color or image to draw on
    * Get image data and every drawn object properties back to Streamlit!
    * Choose to fetch back data in real-time or on demand with a button
    * Undo, Redo, or Drop canvas
    * Save canvas data as JSON to reuse for another session
    """
    )

def full_app():
    st.sidebar.header("Configuration")
    st.markdown(
        """
    Draw on the canvas, get the drawings back to Streamlit!
    * Configure canvas in the sidebar
    * In transform mode, double-click an object to remove it
    * In polygon mode, left-click to add a point, right-click to close the polygon, double-click to remove the latest point
    """
    )

    # Canvas setup
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    if drawing_mode == "point":
        point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
    bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
    realtime_update = st.sidebar.checkbox("Update in realtime", True)

    # Use initial drawing if saved state is checked
    if st.sidebar.checkbox("Initialize with saved state", False):
        with open("saved_state.json", "r") as f:
            initial_drawing = json.load(f)
    else:
        initial_drawing = None

    # Create the canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=realtime_update,
        height=150,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        display_toolbar=st.sidebar.checkbox("Display toolbar", True),
        initial_drawing=initial_drawing,
        key="full_app",
    )

    # Display the drawn image
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)
        
    # Display JSON data of drawn objects
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=["object"]).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)
        
        # Save the current drawing
        if st.sidebar.button("Save Drawing"):
            with open("saved_state.json", "w") as f:
                json.dump(canvas_result.json_data, f)
            st.sidebar.write("Drawing saved!")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Streamlit Drawable Canvas Demo", page_icon=":pencil2:"
    )
    st.title("Drawable Canvas Demo")
    st.sidebar.subheader("Configuration")
    main()
