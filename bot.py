import os
import logging
import requests
import youtube_dl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import Update, ParseMode
from functools import wraps

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Authorized users (you can modify this list with the IDs of authorized users)
AUTHORIZED_USERS = [123456789, 987654321]

# Conversation states
CONFIRM_CANCEL = 0
CANCELLED = 1

def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the video uploader bot! Send me the downloadable links in text format.")


def handle_text(update: Update, context):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        text = update.message.text
        links = text.split()

        for link in links:
            if "youtube.com" in link:
                # Download YouTube video using youtube_dl
                ydl_opts = {
                    'outtmpl': 'video.mp4',
                    'progress_hooks': [progress_hook],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info_dict = ydl.extract_info(link, download=False)
                        video_url = info_dict.get('url', None)

                        if video_url:
                            # Set the video's information as the initial progress
                            progress_message = context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text="📥 Downloading video: {}\n"
                                     "Speed: 0 KB/s\n"
                                     "Progress: 0%\n"
                                     "Remaining time: Calculating..."
                                     .format(info_dict.get('title', 'Unknown'))
                            )

                            # Download the video from the direct link
                            ydl.download([link])

                            # Get the video file name from the link
                            file_name = link.split('/')[-1]

                            # Upload the video file to the Telegram chat
                            context.bot.send_video(
                                chat_id=update.effective_chat.id,
                                video=open(file_name, 'rb'),
                                caption="✅ Download completed: {}".format(info_dict.get('title', 'Unknown'))
                            )

                            # Remove the locally saved video file
                            os.remove(file_name)

                            # Delete the progress message
                            progress_message.delete()
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text=f"Failed to download video from link: {link}")
                    except Exception as e:
                        context.bot.send_message(chat_id=update.effective_chat.id,
                                                 text=f"An error occurred while downloading the video from link: {link}")
                        logging.error(f"Error: {e}")
            else:
                # Download the video from the link
                try:
                    video_file = requests.get(link)

                    # Get the video file name from the link
                    file_name = link.split('/')[-1]

                    # Save the video file locally
                    with open(file_name, 'wb') as f:
                        f.write(video_file.content)

                    # Upload the video file to the Telegram chat
                    context.bot.send_video(chat_id=update.effective_chat.id, video=open(file_name, 'rb'))

                    # Remove the locally saved video file
                    os.remove(file_name)
                except Exception as e:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f"An error occurred while downloading the file from link: {link}")
                    logging.error(f"Error: {e}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You are not authorized to use this bot.")


def progress_hook(progress):
    # Get the current video's information
    title = progress.get('filename', 'Unknown')
    speed = progress.get('speed', None)
    downloaded = progress.get('downloaded_bytes', None)
    total = progress.get('total_bytes', None)
    status = progress.get('status', None)
    eta = progress.get('eta', None)

    if speed is not None and downloaded is not None and total is not None:
        percentage = downloaded / total * 100
        message = "📥 Downloading video: {}\n".format(title)
        message += "Speed: {:.2f} KB/s\n".format(speed / 1024)
        message += "Progress: {:.2f}%\n".format(percentage)
        if eta is not None:
            message += "Remaining time: {}\n".format(format_time(eta))
        message += "Status: {}\n".format(status)
        message += "Note: Please wait for the download to complete before sending another link."

        # Edit the message with the updated progress
        progress_message.edit_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    time = ""
    if hours > 0:
        time += "{:02d}h ".format(hours)
    if minutes > 0:
        time += "{:02d}m ".format(minutes)
    if seconds > 0:
        time += "{:02d}s".format(seconds)
    return time


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context):
        user_id = update.effective_user.id
        if user_id not in AUTHORIZED_USERS:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this bot.")
            return
        return func(update, context)
    return wrapped


@restricted
def cancel(update: Update, context):
    reply_markup = {'keyboard': [['Yes', 'No']], 'one_time_keyboard': True}
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Are you sure you want to cancel? This will stop the current download process.",
                             reply_markup=reply_markup)

    return CONFIRM_CANCEL


@restricted
def confirm_cancel(update: Update, context):
    user_response = update.message.text.lower()

    if user_response == 'yes':
        # TODO: Implement cancellation logic
        context.bot.send_message(chat_id=update.effective_chat.id, text="Download process cancelled.")
        return CANCELLED
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled request aborted.")
        return ConversationHandler.END


def main():
    # Create the Telegram Updater and pass your bot token
    updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN', use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the start command handler
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Register the text message handler
    text_handler = MessageHandler(Filters.text, handle_text)
    dispatcher.add_handler(text_handler)

    # Create a conversation handler for the cancel command
    cancel_handler = ConversationHandler(
        entry_points=[CommandHandler('cancel', cancel)],
        states={
            CONFIRM_CANCEL: [MessageHandler(Filters.regex('^(Yes|No)$'), confirm_cancel)]
        },
        fallbacks=[MessageHandler(Filters.text, handle_text)]
    )
    dispatcher.add_handler(cancel_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
