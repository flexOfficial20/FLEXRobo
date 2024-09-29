#FLEX
from pyrogram import Client, filters
from pytube import YouTube
import instaloader
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("FLEXRobo", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply("Welcome! Send me a YouTube or Instagram link to download videos.")

@app.on_message(filters.regex(r'https?://(www\.)?youtube\.com|youtu\.?be'))
def download_youtube(client, message):
    url = message.text
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        video_file = video.download(filename='video.mp4')
        client.send_document(message.chat.id, video_file)
        os.remove(video_file)  # Cleanup after sending
    except Exception as e:
        message.reply(f"Error: {str(e)}")

@app.on_message(filters.regex(r'https?://(www\.)?instagram\.com'))
def download_instagram(client, message):
    loader = instaloader.Instaloader()
    url = message.text

    try:
        shortcode = url.split("/")[-2]  # Extract shortcode from URL
        loader.download_post(loader.check_post(shortcode), target='')
        video_file = f"{shortcode}.mp4"  # Adjust according to your saving logic
        client.send_document(message.chat.id, video_file)
        os.remove(video_file)  # Cleanup after sending
    except Exception as e:
        message.reply(f"Error: {str(e)}")

if __name__ == "__main__":
    app.run()