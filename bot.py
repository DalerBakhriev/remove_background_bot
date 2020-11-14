import io
import logging
import os
import subprocess
import threading
import time

from aiogram import Bot, Dispatcher, executor, types
from typing import List, Union

from task import remove_image_background

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "")
WAITING_FOR_CELERY_TO_START_TIME_SEC = 10
TASK_TIMEOUT_SEC = 20
CELERY_START_COMMAND = "celery --app task worker --events --loglevel INFO"


bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


def run_command(cmd: Union[str, List[str]]):
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

    logging.info(
        "Got photo from user with user name: %s, first name: %s, last name: %s",
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    photo_buffer = io.BytesIO()
    await message.photo[-1].download(photo_buffer)
    photo_buffer.seek(0)
    photo = photo_buffer.read()

    remove_photo_background_task = remove_image_background.delay(photo)
    await message.reply_photo(remove_photo_background_task.get(timeout=TASK_TIMEOUT_SEC))
    logging.info(
        "Successfully sent photo with removed background to user %s %s",
        message.from_user.first_name,
        message.from_user.last_name
    )

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        level=logging.INFO
    )
    celery_start_thread = threading.Thread(
        target=run_command,
        args=(CELERY_START_COMMAND, )
    )
    logging.info("Starting celery...")
    celery_start_thread.start()
    logging.info("Waiting Celery to start for %d seconds", WAITING_FOR_CELERY_TO_START_TIME_SEC)
    time.sleep(WAITING_FOR_CELERY_TO_START_TIME_SEC)

    logging.info("Starting telegram bot application")
    executor.start_polling(dispatcher, skip_updates=True)
