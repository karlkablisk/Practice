import streamlit as st
from tkinter import Tk, Canvas, NW
import pyscreenshot as ImageGrab
from PIL import Image
from io import BytesIO

# Function to allow the user to select a region of the screen
def select_screen_area():
    root = Tk()
    root.attributes("-alpha", 0.3)  # Make the window transparent
    root.attributes("-topmost", True)  # Keep the window on top
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Create a fullscreen canvas
    canvas = Canvas(root, width=screen_width, height=screen_height)
    canvas.pack()

    # Capture the full screen using pyscreenshot
    full_screenshot = ImageGrab.grab()

    # Convert the screenshot to a format that Tkinter can use
    img = full_screenshot.convert("RGB")
    tk_img = ImageTk.PhotoImage(img)

    # Display the screenshot on the canvas
    canvas.create_image(0, 0, anchor=NW, image=tk_img)

    # Variables to store the selection coordinates
    start_x = start_y = end_x = end_y = 0

    # Function to handle the start of the click-and-drag event
    def on_click(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y

    # Function to handle the release of the click-and-drag event
    def on_release(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        root.quit()

    # Bind the click-and-drag events to the canvas
    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<ButtonRelease-1>", on_release)

    root.mainloop()

    # Close the Tkinter window
    root.destroy()

    # Crop the selected area from the full screenshot
    cropped_img = full_screenshot.crop((start_x, start_y, end_x, end_y))
    return cropped_img

# Streamlit app
st.title("Click-and-Drag Screenshot Capture")

if st.button("Capture Selected Area"):
    selected_img = select_screen_area()
    st.success("Screenshot of selected area captured successfully!")

    # Convert the screenshot to bytes
    img_byte_arr = BytesIO()
    selected_img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    # Display the screenshot in Streamlit
    st.image(img_bytes, caption="Captured Screenshot of Selected Area", use_column_width=True)

    # Provide the screenshot as a downloadable file
    st.download_button(
        label="Download Screenshot",
        data=img_bytes,
        file_name="selected_area_screenshot.png",
        mime="image/png"
    )
