import os
import streamlit as st
from PIL import Image, ImageDraw
import os
import openai

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def draw_rectangle(image_path, coords):
    """Draws a rectangle on the image based on the given coordinates."""
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        draw.rectangle(coords, outline="green", width=5)
        output_path = image_path.replace('.png', '_modified.png')
        img.save(output_path)
    return output_path, coords

def get_gpt_response(prompt):
    """Uses GPT-4o to generate a response based on the input prompt."""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

st.title('Image Text Box Drawer')

uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image_path = f"./temp_{uploaded_file.name}"
    with open(image_path, 'wb') as f:
        f.write(uploaded_file.getvalue())
    
    # Input for rectangle coordinates
    x1 = st.number_input('Enter X1 Coordinate', min_value=0, value=462)
    y1 = st.number_input('Enter Y1 Coordinate', min_value=0, value=80)
    x2 = st.number_input('Enter X2 Coordinate', min_value=0, value=926)
    y2 = st.number_input('Enter Y2 Coordinate', min_value=0, value=146)
    coords = (x1, y1, x2, y2)

    if st.button('Draw Rectangle'):
        modified_image_path, used_coords = draw_rectangle(image_path, coords)
        st.image(modified_image_path, caption='Modified Image with Rectangle')
        st.success(f"Rectangle drawn with coordinates: {used_coords}")

    # GPT-4o prompt input
    prompt = st.text_input("Enter a prompt for GPT-4o")
    if st.button('Get GPT-4o Response'):
        gpt_response = get_gpt_response(prompt)
        st.text_area("GPT-4o Response", gpt_response, height=300)
