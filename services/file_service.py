# backend/services/file_service.py

import os
from .validators import validate_filename
from .schemas import success_response
from .exceptions import NotFoundError


def list_files():
    from .validators import BASE_DATA_PATH

    files = os.listdir(BASE_DATA_PATH)

    return success_response({"files": files})


def read_file(filename: str):
    file_path = validate_filename(filename)

    if not os.path.exists(file_path):
        raise NotFoundError("File not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return success_response({
        "filename": filename,
        "content": content
    })