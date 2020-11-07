import io
import logging
import os
import subprocess
import threading
import time

from aiogram import Bot, Dispatcher, executor, types

from task import remove_image_background

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "")
WAITING_FOR_CELERY_TO_START_TIME_SEC = 10

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


def start_celery(cmd: str):
    subprocess.run(cmd, shell=True)


@dispatcher.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):

    """
    Welcome message for user
    """

    await message.answer(
        "Hi!\nI'm RemoveBackgroundBot!\n"
        "Send me photo and i will send you this photo with removed background"
    )


@dispatcher.message_handler(content_types=["photo"])
async def send_image_with_removed_background(message: types.Message):

    """
    Sends back image that user has sent to bot with removed background
    :param message: message from user (uploaded photo)
    """

    logging.info("Got photo from user")
    photo_buffer = io.BytesIO()
    logging.info("Uploading photo...")
    await message.photo[-1].download(photo_buffer)
    logging.info("Successfully uploaded photo...")
    photo_buffer.seek(0)
    photo = photo_buffer.read()

    logging.info("Sending task to celery")
    remove_photo_background_task = remove_image_background.delay(photo)
    await message.reply_photo(remove_photo_background_task.get())

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        level=logging.INFO
    )
    celery_start_thread = threading.Thread(
        target=start_celery,
        args=("celery --app task worker --events --pool solo --loglevel WARNING", )
    )
    logging.info("Starting celery...")
    celery_start_thread.start()
    logging.info("Waiting Celery to start for %d seconds", WAITING_FOR_CELERY_TO_START_TIME_SEC)
    time.sleep(WAITING_FOR_CELERY_TO_START_TIME_SEC)

    logging.info("Starting telegram bot application")
    executor.start_polling(dispatcher, skip_updates=True)
