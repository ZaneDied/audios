from pytubefix import YouTube
import requests

url = "https://youtu.be/EZE62LpaqHg?si=MokKOHEBHWcIi4RY"
yt = YouTube(url)

# Get the thumbnail URL
thumb_url = yt.thumbnail_url

# Download the image
response = requests.get(thumb_url, verify=False)
if response.status_code == 200:
    # Save the file (usually .jpg or .webp)
    with open("thumbnail.jpg", "wb") as f:
        f.write(response.content)
    print("Thumbnail downloaded successfully!")