import logging
import os

from celery import Celery
from background_remover.bg import remove

RABBIT_URL = os.getenv("CLOUDAMQP_URL", "amqp://")

app = Celery("task", broker=RABBIT_URL, backend="rpc://")
app.config_from_object("celery_config")


@app.task(serializer="pickle")
def remove_image_background(image: bytes) -> bytes:

    """
    Return image with removed background
    :param image: image to remove background on
    :return: image with removed background
    """

    logging.info("Starting to remove background from photo")
    image_with_removed_background = remove(image, model_name="u2netp")
    logging.info("Successfully removed background")

    return image_with_removed_background
