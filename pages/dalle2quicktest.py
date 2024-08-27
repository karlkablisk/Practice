import streamlit as st
import os
import openai
from io import BytesIO
import base64
from PIL import Image

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

st.title("DALL-E 2 Image Generator")

# Prompt for user input
prompt = st.text_input("Enter a prompt for the image generation", 
                       value="A futuristic city skyline at sunset")

if st.button("Generate Image"):
    st.write("Generating image...")
    
    # Set up the image parameters
    image_params = {
        "model": "dall-e-2",
        "n": 1,
        "size": "1024x1024",
        "prompt": prompt,
        "response_format": "b64_json",
    }

    # Generate the image
    try:
        images_response = client.images.generate(**image_params)
        image_data = images_response.data[0].b64_json
        
        # Convert the base64-encoded image data to a PIL Image
        image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Display the image in Streamlit
        st.image(image, caption="Generated Image", use_column_width=True)

        # Save the image file
        image.save("generated_image.png")
        st.write("Image saved as generated_image.png")

    except openai.APIConnectionError as e:
        st.error(f"Server connection error: {e}")
    except openai.RateLimitError as e:
        st.error(f"OpenAI rate limit error: {e}")
    except openai.APIStatusError as e:
        st.error(f"OpenAI status error: {e}")
    except openai.BadRequestError as e:
        st.error(f"OpenAI bad request error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
