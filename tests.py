import hashlib
import random
import string
from typing import Dict, Union
from background_remover.bg import remove

import multiprocessing
from task import remove_image_background
import time
from bot import CELERY_START_COMMAND, run_command

import pytest


def generate_random_string(length: int) -> str:

    """
    Generates random string with specified length
    :param length: length of generated string
    :return: random string with specified length
    """

    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for _ in range(length))

    return random_string


@pytest.fixture
def celery_worker_parameters() -> Dict[str, bool]:

    """
    Redefine this fixture to change the init parameters of Celery workers.

    This can be used e. g. to define queues the worker will consume tasks from.

    The dict returned by your fixture will then be used
    as parameters when instantiating :class:`~celery.worker.WorkController`.
    """

    return {
        # For some reason this `celery.ping` is not registered IF our own worker is still
        # running. To avoid failing tests in that case, we disable the ping check.
        # see: https://github.com/celery/celery/issues/3642#issuecomment-369057682
        # here is the ping task: `from celery.contrib.testing.tasks import ping`
        "perform_ping_check": False,
    }


@pytest.fixture(scope="function")
def random_string():
    return generate_random_string(random.choice(list(range(50, 101))))


@pytest.fixture(scope="function")
def image_for_test():
    with open("test_files/test_img.jpg", "rb") as test_file:
        test_image = test_file.read()
    return test_image


@pytest.fixture(scope="function")
def celery_image_app():
    celery_start_process = multiprocessing.Process(
        target=run_command,
        args=(CELERY_START_COMMAND,)
    )
    celery_start_process.start()
    time.sleep(5)
    print("Started celery for test")
    yield
    celery_start_process.terminate()


def test_simple_hash_task(celery_app, celery_worker, random_string):

    @celery_app.task
    def calculate_hash_sha256(some_random_string: Union[str, bytes]) -> str:
        return hashlib.sha256(some_random_string.encode("utf-8")).hexdigest()

    # Reload worker to add test_task to its registry.
    celery_worker.reload()

    calculate_hash_task = calculate_hash_sha256.delay(random_string)
    result_from_celery = calculate_hash_task.get(timeout=3)
    result = hashlib.sha256(random_string.encode()).hexdigest()
    assert result_from_celery == result


def test_remove_background_task(celery_image_app, image_for_test):

    remove_image_background_task = remove_image_background.delay(image_for_test)
    result_from_celery = remove_image_background_task.get(timeout=5)
    result = remove(image_for_test, model_name="u2netp").tobytes()
    assert result_from_celery == result

