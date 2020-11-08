import logging

from celery import Celery
from rembg.bg import remove

app = Celery("task", broker="redis://localhost", backend="rpc://")
app.config_from_object("celery_config")


@app.task(serializer="pickle")
def remove_image_background(image: bytes) -> bytes:

    """
    Return image with removed background
    :param image: image to remove background on
    :return: image with removed background
    """

    logging.info("Starting to remove background from photo")
    image_with_removed_background = remove(image)
    logging.info("Successfully removed background")

    return image_with_removed_background.tobytes()

