def build_trip_prompt(
    request,
    context="",
    weather_context="",
    feedback=""
):
    return f"""
你是 GeoTrip 的旅行规划助手。

请根据以下用户信息生成旅行计划：

目的地：{request.destination}
旅行天数：{request.days}
预算：{request.budget} 元
交通方式：{request.transport}
兴趣：{", ".join(request.interests)}
旅行月份：{request.travel_month}
出发日期：{request.start_date.isoformat()}
以下是从旅行知识库中检索到的参考信息：

--- 知识库开始 ---

{context}

--- 知识库结束 ---

以下是通过外部工具获取的天气信息：

--- 天气信息开始 ---

{weather_context}

--- 天气信息结束 ---

如果天气信息存在，请结合真实天气情况调整旅行安排。
如果天气条件不适合某些户外活动，请降低相关活动强度或安排替代方案。

请优先参考知识库中的信息生成旅行计划。
如果知识库中的信息与本次旅行相关，请合理融入行程。
不要编造与知识库信息明显冲突的内容。

{feedback}

请严格按照 JSON 格式返回，不要输出 JSON 以外的任何文字。
所有文本内容使用中文。

必须严格生成 {request.days} 天行程，不得多于或少于该天数。

格式如下：

{{
    "destination": "{request.destination}",
    "days": [
        {{
            "day": 1,
            "title": "当天行程标题",
            "activities": [
                "活动1",
                "活动2"
            ]
        }}
    ]
}}
"""