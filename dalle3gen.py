import requests
from io import BytesIO
from PIL import Image


class Dalle3Generator:
    def __init__(self, client):
        self.client = client

    def generate_image(self, prompt, size="1024x1024", quality="standard"):
        image_params = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1,
        }

        try:
            images_response = self.client.images.generate(**image_params)
            image_url = images_response.data[0].url
            response = requests.get(image_url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))

        except Exception as e:
            print(f"Failed to generate image: {e}")
            raise

    def save_image(self, image, filename):
        image.save(filename)
        print(f"Image saved as {filename}")
