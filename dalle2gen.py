import base64
from io import BytesIO
from PIL import Image
import requests


class Dalle2Generator:
    def __init__(self, client):
        self.client = client

    def generate_image(self, prompt, size="1024x1024", response_format="b64_json"):
        image_params = {
            "model": "dall-e-2",
            "n": 1,
            "size": size,
            "prompt": prompt,
            "response_format": response_format,
        }

        try:
            images_response = self.client.images.generate(**image_params)
            if response_format == "b64_json":
                image_data = images_response.data[0].b64_json
                return Image.open(BytesIO(base64.b64decode(image_data)))
            else:
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
