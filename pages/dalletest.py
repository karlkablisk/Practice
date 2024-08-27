import os
import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Streamlit UI setup
st.title("DALL·E Image Generation with OpenAI")
st.write("Generate images using DALL·E based on text, images, or a combination of both.")

# Dropdown options
models = ["DALL·E 3", "DALL·E 2"]
qualities = ["Standard", "HD"]
resolutions = {
    "1024×1024": "$0.040 / image",
    "1024×1792": "$0.080 / image",
    "1792×1024": "$0.080 / image",
    "512×512": "$0.018 / image",
    "256×256": "$0.016 / image"
}

# User selections
selected_model = st.selectbox("Select DALL·E Model", models)
selected_quality = st.selectbox("Select Image Quality", qualities)
selected_resolution = st.selectbox("Select Image Resolution", list(resolutions.keys()))

# Determine the price based on the selected options
price_mapping = {
    ("DALL·E 3", "Standard", "1024×1024"): "$0.040 / image",
    ("DALL·E 3", "Standard", "1024×1792"): "$0.080 / image",
    ("DALL·E 3", "Standard", "1792×1024"): "$0.080 / image",
    ("DALL·E 3", "HD", "1024×1024"): "$0.080 / image",
    ("DALL·E 3", "HD", "1024×1792"): "$0.120 / image",
    ("DALL·E 3", "HD", "1792×1024"): "$0.120 / image",
    ("DALL·E 2", "1024×1024"): "$0.020 / image",
    ("DALL·E 2", "512×512"): "$0.018 / image",
    ("DALL·E 2", "256×256"): "$0.016 / image"
}

# Display the price
price = price_mapping.get((selected_model, selected_quality, selected_resolution), "Unknown")
st.write(f"Price: {price}")

# Option 1: Text-to-Image
st.header("Option 1: Text-to-Image")
text_prompt = st.text_input("Enter a text prompt for image generation:")
if st.button("Generate Image from Text"):
    if text_prompt:
        try:
            response = client.images.generate(
                model=selected_model.lower().replace(" ", "-"),
                prompt=text_prompt,
                size=selected_resolution.replace("×", "x"),
                quality=selected_quality.lower(),
                n=1
            )
            image_url = response.data[0].url
            image = Image.open(BytesIO(requests.get(image_url).content))
            st.image(image, caption="Generated Image from Text", use_column_width=True)
        except Exception as e:
            st.error(f"Failed to generate image: {e}")
    else:
        st.warning("Please enter a text prompt.")

# Option 2: Image-based Generation (Outpainting)
st.header("Option 2: Image and Text-based Generation")
uploaded_file = st.file_uploader("Upload an image to modify:")
additional_text_prompt = st.text_input("Enter additional text for image generation:")
if st.button("Generate Image from Image and Text"):
    if uploaded_file and additional_text_prompt:
        try:
            image_bytes = uploaded_file.read()
            response = client.images.edit(
                model="dall-e-2",  # Image edits (inpainting) are DALL·E 2 specific
                image=image_bytes,
                prompt=additional_text_prompt,
                size=selected_resolution.replace("×", "x"),
                n=1
            )
            image_url = response.data[0].url
            modified_image = Image.open(BytesIO(requests.get(image_url).content))
            st.image(modified_image, caption="Modified Image based on Input", use_column_width=True)
        except Exception as e:
            st.error(f"Failed to generate image: {e}")
    else:
        st.warning("Please upload an image and enter a text prompt.")

# Option 3: Inpainting
st.header("Option 3: Inpainting (Image Editing)")
inpainting_file = st.file_uploader("Upload an image for inpainting (select an area to modify):")
inpainting_text_prompt = st.text_input("Enter a text prompt for inpainting:")
if st.button("Inpaint Image"):
    if inpainting_file and inpainting_text_prompt:
        try:
            image_bytes = inpainting_file.read()
            response = client.images.edit(
                model="dall-e-2",  # Inpainting is specific to DALL·E 2
                image=image_bytes,
                prompt=inpainting_text_prompt,
                size=selected_resolution.replace("×", "x"),
                n=1
            )
            inpainted_image = Image.open(BytesIO(requests.get(response.data[0].url).content))
            st.image(inpainted_image, caption="Inpainted Image", use_column_width=True)
        except Exception as e:
            st.error(f"Failed to inpaint image: {e}")
    else:
        st.warning("Please upload an image and enter a text prompt.")

# Explanation of Inpainting
st.header("Explanation: Inpainting vs. Image Modification")
st.write("""
- **Text-to-Image**: Generates an entirely new image based on the text prompt provided.
- **Image and Text-based Generation**: Modifies or extends the uploaded image based on the provided text.
- **Inpainting**: Edits or fills in specific areas of the uploaded image based on the text prompt. 
  Inpainting typically involves providing
