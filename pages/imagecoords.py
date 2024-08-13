import os
import base64
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from openai import OpenAI

# Models for text generation
gpt35 = "gpt-3.5-turbo"
gpt4t = "gpt-4-turbo"
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

# Set the default model here
default_model = gptop

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def draw_rectangle(self, image_path, coords):
        """Draws a rectangle on the image based on the given coordinates."""
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            draw.rectangle(coords, outline="green", width=1)  # Set stroke width to 1
            output_path = image_path.replace('.png', '_modified.png')
            img.save(output_path)
        return output_path, coords

    def encode_image(self, image_path):
        """Encodes an image file as a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def generate_text(self, prompt, model, image_path=None):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        if image_path:
            base64_image = self.encode_image(image_path)
            messages = [
                {"role": "system", "content": "You are a helpful assistant that can analyze images and respond in Markdown."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"}  # This passes the image to the AI
                    }
                ]}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=150
        )
        return response.choices[0].message.content

    def run(self):
        st.title('Image Text Box Drawer, Text Generator, and Rectangle Highlighter')

        uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image_path = f"./temp_{uploaded_file.name}"
            with open(image_path, 'wb') as f:
                f.write(uploaded_file.getvalue())

            # Load the image to get its dimensions
            image = Image.open(image_path)
            img_width, img_height = image.size

            st.subheader("Draw to Highlight")
            drawing_mode = st.selectbox(
                "Drawing tool:",
                ("rect", "circle", "transform"),
            )
            stroke_color = st.color_picker("Stroke color hex: ")

            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                stroke_width=1,  # Fixed stroke width
                stroke_color=stroke_color,
                background_image=image,  # Set the uploaded image as background
                update_streamlit=True,
                height=img_height,  # Match the canvas size to the image dimensions
                width=img_width,
                drawing_mode=drawing_mode,
                display_toolbar=True,
                key="draw_to_highlight",
            )

            # Show the drawn rectangles' coordinates
            if canvas_result.json_data is not None:
                objects = pd.json_normalize(canvas_result.json_data["objects"])
                st.dataframe(objects[['left', 'top', 'width', 'height']])
                st.success("Coordinates of drawn rectangles have been extracted.")

        # Dropdown for model selection with gptop as the default
        model_choice = st.selectbox(
            "Choose GPT Model:", 
            [gpt35, gpt4t, gpto, gptop, gptomini],
            index=[gpt35, gpt4t, gpto, gptop, gptomini].index(default_model)  # Easy default model selection
        )

        prompt_text = st.text_area("Enter your prompt:", value="Highlight the dialog area.")
        if st.button("Generate Text"):
            if not prompt_text.strip():
                st.error("Please enter some prompt text.")
            else:
                try:
                    generated_text = self.generate_text(prompt_text, model_choice, image_path if uploaded_file else None)
                    st.text_area("Generated Text:", value=generated_text, height=300)
                    st.success("Text generated successfully.")
                except Exception as e:
                    st.error(f"Error generating text: {e}")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
