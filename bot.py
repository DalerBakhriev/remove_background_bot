import io
import logging
import os
import subprocess
from rembg.bg import remove

from aiogram import Bot, Dispatcher, executor, types


API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "")


bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


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

    photo_with_removed_background = remove(photo).tobytes()
    await message.reply_photo(photo_with_removed_background)
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

    logging.info("Starting telegram bot application")
    executor.start_polling(dispatcher, skip_updates=True)
