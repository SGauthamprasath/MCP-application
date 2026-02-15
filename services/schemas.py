
def success_response(data: dict):
    return {
        "status": "success",
        "data": data
    }


def error_response(message: str):
    return {
        "status": "error",
        "message": message
    }