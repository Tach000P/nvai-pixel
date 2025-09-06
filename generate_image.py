from g4f.client import Client
import requests

def generate_image(prompt: str):
    client = Client()
    response = client.images.generate(
        model="flux",
        prompt=prompt,
        response_format="url"
    )

    download_image(response.data[0].url)

def download_image(image_url):

    response = requests.get(image_url)

    with open('image.jpg', 'wb') as file:
        file.write(response.content)

    print('Download Completed')
