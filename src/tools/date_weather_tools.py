"""Custom tools for weather and date agents."""

from datetime import datetime
import random


def get_current_date() -> str:
    """Get the current date and time.

    Returns:
        str: Current date and time in a human-readable format.
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


def get_current_weather(location: str) -> str:
    """Get the current weather for a given location.

    This is a mock function that returns simulated weather data.
    In a real application, you would integrate with a weather API.

    Args:
        location: The city or location to get weather for.

    Returns:
        str: Weather information for the location.
    """
    # Mock weather conditions
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Stormy", "Snowy"]
    temperatures = list(range(15, 35))

    condition = random.choice(conditions)
    temp = random.choice(temperatures)
    humidity = random.randint(30, 90)
    wind_speed = random.randint(5, 30)

    weather_report = f"""Weather for {location}:
- Condition: {condition}
- Temperature: {temp}°C
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h"""

    return weather_report


def get_date_info(date_query: str) -> str:
    """Get information about dates, including day of week, days until, etc.

    Args:
        date_query: A description of what date information is needed.

    Returns:
        str: Information about the requested date.
    """
    now = datetime.now()

    if "today" in date_query.lower():
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
    elif "tomorrow" in date_query.lower():
        tomorrow = datetime(now.year, now.month, now.day + 1) if now.day < 28 else now
        return f"Tomorrow is {tomorrow.strftime('%A, %B %d, %Y')}"
    elif "day of week" in date_query.lower() or "what day" in date_query.lower():
        return f"Today is {now.strftime('%A')}"
    else:
        return f"Current date: {now.strftime('%A, %B %d, %Y')}"
