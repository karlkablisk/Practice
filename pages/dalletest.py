import os
import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests

# Add the root directory to the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the DALL-E 2 and DALL-E 3 generator classes
from dalle2gen import Dalle2Generator
from dalle3gen import Dalle3Generator

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Initialize the generators
dalle2_generator = Dalle2Generator(client)
dalle3_generator = Dalle3Generator(client)

# Streamlit UI setup
st.title("DALL·E Image Generation with OpenAI")
st.write("Generate images using DALL·E based on text, images, or a combination of both.")

# Combined dropdown options for all valid combinations
options = {
    "DALL·E 3 - Standard - 1024×1024": {"model": "dall-e-3", "quality": "standard", "size": "1024x1024"},
    "DALL·E 3 - Standard - 1024×1792": {"model": "dall-e-3", "quality": "standard", "size": "1024x1792"},
    "DALL·E 3 - Standard - 1792×1024": {"model": "dall-e-3", "quality": "standard", "size": "1792x1024"},
    "DALL·E 3 - HD - 1024×1024": {"model": "dall-e-3", "quality": "hd", "size": "1024x1024"},
    "DALL·E 3 - HD - 1024×1792": {"model": "dall-e-3", "quality": "hd", "size": "1024x1792"},
    "DALL·E 3 - HD - 1792×1024": {"model": "dall-e-3", "quality": "hd", "size": "1792x1024"},
    "DALL·E 2 - 1024×1024": {"model": "dall-e-2", "quality": None, "size": "1024x1024"},
    "DALL·E 2 - 512×512": {"model": "dall-e-2", "quality": None, "size": "512x512"},
    "DALL·E 2 - 256×256": {"model": "dall-e-2", "quality": None, "size": "256x256"},
}

# User selection
selected_option = st.selectbox("Select Model, Quality, and Resolution", list(options.keys()))
selected_config = options[selected_option]

# Display the price based on the selection
price_mapping = {
    "DALL·E 3 - Standard - 1024×1024": "$0.040 / image",
    "DALL·E 3 - Standard - 1024×1792": "$0.080 / image",
    "DALL·E 3 - Standard - 1792×1024": "$0.080 / image",
    "DALL·E 3 - HD - 1024×1024": "$0.080 / image",
    "DALL·E 3 - HD - 1024×1792": "$0.120 / image",
    "DALL·E 3 - HD - 1792×1024": "$0.120 / image",
    "DALL·E 2 - 1024×1024": "$0.020 / image",
    "DALL·E 2 - 512×512": "$0.018 / image",
    "DALL·E 2 - 256×256": "$0.016 / image"
}

# Display the price
price = price_mapping.get(selected_option, "Unknown")
st.write(f"Price: {price}")

# Function to convert images to RGBA format and save as PNG
def convert_image_to_png(image):
    if image.mode in ['RGBA', 'LA', 'L']:
        pass  # Image is already in a valid format
    else:
        image = image.convert('RGBA')  # Convert to RGBA

    with BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()

# Option 1: Text-to-Image
st.header("Option 1: Text-to-Image")
text_prompt = st.text_input("Enter a text prompt for image generation:")
if st.button("Generate Image from Text"):
    if text_prompt:
        try:
            if selected_config["model"] == "dall-e-3":
                image = dalle3_generator.generate_image(
                    prompt=text_prompt, 
                    size=selected_config["size"], 
                    quality=selected_config["quality"]
                )
            elif selected_config["model"] == "dall-e-2":
                image = dalle2_generator.generate_image(
                    prompt=text_prompt, 
                    size=selected_config["size"]
                )
            
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
            # Open the uploaded image file
            image = Image.open(uploaded_file)
            
            # Convert the image to PNG with RGBA format
            image_bytes = convert_image_to_png(image)

            response = client.images.edit(
                model="dall-e-2",  # Image edits (inpainting) are DALL·E 2 specific
                image=image_bytes,
                prompt=additional_text_prompt,
                size=selected_config["size"],
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
            # Open the uploaded image file
            image = Image.open(inpainting_file)
            
            # Convert the image to PNG with RGBA format
            image_bytes = convert_image_to_png(image)

            response = client.images.edit(
                model="dall-e-2",  # Inpainting is specific to DALL·E 2
                image=image_bytes,
                prompt=inpainting_text_prompt,
                size=selected_config["size"],
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
  Inpainting typically involves providing a mask or indicating which part of the image to modify.
""")
