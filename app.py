#FLEX
import os
import logging
from dotenv import load_dotenv
from pyrogram import Client, filters
from pytube import YouTube
import instaloader
import time

# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

app = Client("FLEXRobo", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply("Welcome! Send me a YouTube or Instagram link to download videos.")

@app.on_message(filters.regex(r'https?://(www\.)?youtube\.com|youtu\.?be'))
def download_youtube(client, message):
    url = message.text.strip()
    logging.info(f"Attempting to download video from URL: {url}")
    
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        logging.info(f"Found video: {yt.title}, downloading...")
        video_file = video.download(filename='video.mp4')
        client.send_document(message.chat.id, video_file)
        os.remove(video_file)
        logging.info(f"Downloaded YouTube video: {url}")
    except Exception as e:
        logging.error(f"Error downloading YouTube video: {str(e)}")
        message.reply(f"Error: {str(e)}")

@app.on_message(filters.regex(r'https?://(www\.)?instagram\.com'))
def download_instagram(client, message):
    loader = instaloader.Instaloader()
    loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)  # Authenticate

    url = message.text
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target='')

        video_file = f"{shortcode}.mp4"
        if os.path.exists(video_file):
            client.send_document(message.chat.id, video_file)
            os.remove(video_file)
            logging.info(f"Downloaded Instagram post: {url}")
        else:
            message.reply("No video found in this post.")
    except Exception as e:
        logging.error(f"Error downloading Instagram post: {str(e)}")
        message.reply(f"Error: {str(e)}")

if __name__ == "__main__":
    logging.info("Bot is starting...")
    app.run()