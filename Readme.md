Telegram Video Uploader Bot

This is a Telegram bot that can download and upload videos from downloadable links. It supports both direct video links and YouTube video links.

Features

1. Download videos from direct links and YouTube links.
2. Upload the downloaded videos to the Telegram chat.
3. Show download progress with download speed, percentage, and estimated remaining time.
4. Error handling for failed download.
5. User authentication to restrict bot usage to authorized users.
6. Cancelation of ongoing downloads.


Prerequisites

Python 3.7 or higher
Required Python packages listed in requirements.txt


Getting Started

1. Clone the repository: to services like Heroku.
   git clone link of the repository

2. Install the required packages:
   pip install -r requirements.txt

3. Obtain a Telegram bot token:
   Create a new Telegram bot using BotFather.
   Copy the bot token.
   
5. Set up the bot token:
   Open bot.py file.
   Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token.
   
7. Run the bot:
   python bot.py
   
9. Start the bot in a Telegram chat:
   Open the chat with your bot.
   Send the /start command.
   Follow the bot's instructions to send downloadable links.


   
Deploying to Heroku

1. Sign up for a Heroku account (if you haven't already).
2. Create a new Heroku app.
3. Connect the Heroku app to your GitHub repository.
4. Configure the necessary environment variables:
5. Set the TOKEN environment variable to your Telegram bot token.
Deploy the Heroku app.


