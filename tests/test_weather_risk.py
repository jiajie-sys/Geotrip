from app.tools.weather_risk import evaluate_weather_risk


def test_high_weather_risk():
    weather = {
        "precipitation_probability": 90,
        "wind_speed_max": 65,
        "temperature_min": -2,
        "temperature_max": 5
    }

    result = evaluate_weather_risk(weather)

    assert result["level"] == "high"
    assert result["score"] == 5
    assert result["should_replan"] is True


def test_medium_weather_risk():
    weather = {
        "precipitation_probability": 50,
        "wind_speed_max": 20,
        "temperature_min": 5,
        "temperature_max": 10
    }

    result = evaluate_weather_risk(weather)

    assert result["level"] == "medium"
    assert result["score"] == 1
    assert result["should_replan"] is False


def test_low_weather_risk():
    weather = {
        "precipitation_probability": 10,
        "wind_speed_max": 12,
        "temperature_min": 6,
        "temperature_max": 12
    }

    result = evaluate_weather_risk(weather)

    assert result["level"] == "low"
    assert result["score"] == 0
    assert result["should_replan"] is False