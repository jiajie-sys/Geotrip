import requests
from datetime import date

def get_coordinates(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "zh",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("results")

    if not results:
        raise ValueError(f"找不到城市：{city}")

    location = results[0]

    return {
        "name": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "country": location.get("country")
    }

def get_weather(
    latitude: float,
    longitude: float
):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto",
        "forecast_days": 16
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()

def get_city_weather(
    city: str,
    target_date: date
):
    location = get_coordinates(city)

    weather_data = get_weather(
        latitude=location["latitude"],
        longitude=location["longitude"]
    )

    daily = weather_data.get(
        "daily",
        {}
    )

    dates = daily.get("time", [])

    target_date_string = (
        target_date.isoformat()
    )

    if target_date_string not in dates:
        raise ValueError(
            f"没有 {target_date_string} 的天气预报"
        )

    index = dates.index(
        target_date_string
    )

    return {
        "city": location["name"],
        "country": location["country"],
        "date": target_date_string,
        "temperature_max": (
            daily["temperature_2m_max"][index]
        ),
        "temperature_min": (
            daily["temperature_2m_min"][index]
        ),
        "precipitation_probability": (
            daily[
                "precipitation_probability_max"
            ][index]
        ),
        "wind_speed_max": (
            daily["wind_speed_10m_max"][index]
        )
    }


def should_use_weather_tool(start_date: date):
    today = date.today()

    days_until_trip = (
        start_date - today
    ).days

    if days_until_trip < 0:
        return False

    if days_until_trip > 16:
        return False

    return True