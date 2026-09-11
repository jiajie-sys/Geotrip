weather_tool = {
    "type": "function",
    "function": {
        "name": "get_city_weather",
        "description": "获取指定城市在指定日期的天气预报，用于旅行规划。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如 Reykjavik"
                },
                "target_date": {
                    "type": "string",
                    "description": "目标日期，格式 YYYY-MM-DD，例如 2026-09-15"
                }
            },
            "required": [
                "city",
                "target_date"
            ]
        }
    }
}