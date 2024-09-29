#FLEX
import os
import logging
import requests
from dotenv import load_dotenv
from pyrogram import Client, filters
from pytube import YouTube
import instaloader
from pyrogram.errors import FloodWait

# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

app = Client("FLEXRobo", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def send_message(chat_id, text):
    while True:
        try:
            await app.send_message(chat_id, text)
            break
        except FloodWait as e:
            logging.warning(f"Flood wait: sleeping for {e.x} seconds.")
            await asyncio.sleep(e.x)

@app.on_message(filters.command("start"))
async def start(client, message):
    await send_message(message.chat.id, "Welcome! Send me a YouTube or Instagram link to download videos.")

@app.on_message(filters.regex(r'https?://(www\.)?youtube\.com|youtu\.?be'))
async def download_youtube(client, message):
    url = message.text.strip()
    video_id = url.split('v=')[-1] if 'v=' in url else url.split('/')[-1]
    
    logging.info(f"Attempting to download YouTube video from URL: {url}")
    
    # YouTube API call
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        await send_message(message.chat.id, "Error fetching video details. Please check the video URL.")
        return

    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        logging.info(f"Found video: {yt.title}, downloading...")
        video_file = video.download(filename='video.mp4')
        await app.send_document(message.chat.id, video_file)
        os.remove(video_file)
        logging.info(f"Downloaded YouTube video: {url}")
    except Exception as e:
        logging.error(f"Error downloading YouTube video: {str(e)}")
        await send_message(message.chat.id, f"Error: {str(e)}")

@app.on_message(filters.regex(r'https?://(www\.)?instagram\.com'))
async def download_instagram(client, message):
    loader = instaloader.Instaloader()

    # Automated login
    try:
        loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)  # Perform automatic login
        logging.info(f"Logged in to Instagram as {INSTAGRAM_USERNAME}")
    except instaloader.exceptions.LoginException as e:
        logging.error(f"Login failed: {str(e)}")
        await send_message(message.chat.id, "Login failed. Please check your credentials.")
        return

    url = message.text.strip()
    logging.info(f"Attempting to download Instagram post from URL: {url}")

    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target='')

        video_file = f"{shortcode}.mp4"
        if os.path.exists(video_file):
            await app.send_document(message.chat.id, video_file)
            os.remove(video_file)
            logging.info(f"Downloaded Instagram post: {url}")
        else:
            await send_message(message.chat.id, "No video found in this post.")
    except Exception as e:
        logging.error(f"Error downloading Instagram post: {str(e)}")
        await send_message(message.chat.id, f"Error: {str(e)}")

if __name__ == "__main__":
    logging.info("Bot is starting...")
    app.run()