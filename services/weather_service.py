
import random
from .validators import validate_city
from .schemas import success_response
from .exceptions import ValidationError


def get_weather(city: str) -> dict:
    validate_city(city)

    # MOCK MODE (safe workshop backup)
    weather_data = {
        "city": city,
        "temperature_celsius": round(random.uniform(20, 35), 2),
        "humidity": random.randint(40, 80),
        "condition": random.choice(["Sunny", "Cloudy", "Rainy"])
    }

    return success_response(weather_data)