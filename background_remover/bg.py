import io

import functools
import numpy as np
from PIL import Image

from .u2net import detect


def naive_cutout(img, mask):
    empty = Image.new("RGBA", img.size, 0)
    cutout = Image.composite(img, empty, mask.resize(img.size, Image.LANCZOS))
    return cutout


@functools.lru_cache(maxsize=None)
def get_model(model_name):
    if model_name == "u2netp":
        return detect.load_model(model_name="u2netp")
    else:
        return detect.load_model(model_name="u2net")


def remove(data: bytes, model_name: str = "u2net") -> bytes:
    model = get_model(model_name)
    img = Image.open(io.BytesIO(data)).convert("RGB")
    mask = detect.predict(model, np.array(img)).convert("L")

    cutout = naive_cutout(img, mask)

    bio = io.BytesIO()
    cutout.save(bio, "PNG")

    return bio.getbuffer().tobytes()
