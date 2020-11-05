import io
import os

from aiogram import Bot, Dispatcher, executor, types

from task import remove_image_background

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN", "")
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):

    """
    Welcome message for user
    """

    await message.reply(
        "Hi!\nI'm RemoveBackgroundBot!\n"
        "Send me photo and i will send you this photo with removed background"
    )


@dispatcher.message_handler(content_types=["photo"])
async def send_image_with_removed_background(message: types.Message):

    """
    Sends back image that user has sent to bot with removed background
    :param message: message from user (uploaded photo)
    """

    photo_buffer = io.BytesIO()
    await message.photo[-1].download(photo_buffer)
    photo_buffer.seek(0)
    photo_with_removed_background = remove_image_background.delay(photo_buffer.read())

    await message.reply_photo(photo_with_removed_background.get())


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=True)
