def evaluate_weather_risk(weather: dict):
    precipitation = weather.get(
        "precipitation_probability",
        0
    )

    wind_speed = weather.get(
        "wind_speed_max",
        0
    )

    temperature_min = weather.get(
        "temperature_min",
        0
    )

    risk_score = 0
    reasons = []

    if precipitation >= 70:
        risk_score += 2
        reasons.append(
            f"降水概率较高：{precipitation}%"
        )

    elif precipitation >= 40:
        risk_score += 1
        reasons.append(
            f"存在一定降水概率：{precipitation}%"
        )

    if wind_speed >= 50:
        risk_score += 2
        reasons.append(
            f"最大风速较高：{wind_speed} km/h"
        )

    elif wind_speed >= 30:
        risk_score += 1
        reasons.append(
            f"风力较明显：{wind_speed} km/h"
        )

    if temperature_min <= 0:
        risk_score += 1
        reasons.append(
            f"最低温度较低：{temperature_min}°C"
        )

    if risk_score >= 3:
        level = "high"
        should_replan = True

    elif risk_score >= 1:
        level = "medium"
        should_replan = False

    else:
        level = "low"
        should_replan = False

    return {
        "level": level,
        "score": risk_score,
        "should_replan": should_replan,
        "reasons": reasons
    }