
import os
from .exceptions import ValidationError, FileAccessError

BASE_DATA_PATH = "C:\\Users\\gauth\\yukta-2k26\\MCP-application\\data"


def validate_city(city: str):
    if not city or not isinstance(city, str):
        raise ValidationError("Invalid city name")


def validate_filename(filename: str):
    if ".." in filename:
        raise FileAccessError("Directory traversal detected")

    full_path = os.path.abspath(os.path.join(BASE_DATA_PATH, filename))

    if not full_path.startswith(BASE_DATA_PATH):
        raise FileAccessError("Access outside data directory is forbidden")

    return full_path