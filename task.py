from celery import Celery
from rembg.bg import remove

app = Celery("task")
app.config_from_object("celeryconfig")


@app.task(serializer="pickle")
def remove_image_background(image: bytes) -> bytes:

    """
    Return image with removed background
    :param image: image to remove background on
    :return: image with removed background
    """

    image_with_removed_background_buffer = remove(image)

    return image_with_removed_background_buffer
