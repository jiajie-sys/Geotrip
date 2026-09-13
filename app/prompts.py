def build_trip_prompt(
    request,
    context="",
    weather_context="",
    places_context="",
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

以下是从结构化景点数据库中获取的参考信息：

--- 景点信息开始 ---

{places_context}

--- 景点信息结束 ---

如果景点信息存在，请优先从这些结构化景点中选择适合用户兴趣和旅行天数的地点。
不要编造与景点数据库明显冲突的具体景点信息。

--- 天气信息开始 ---

{weather_context}

--- 天气信息结束 ---

如果天气信息存在，请结合真实天气情况调整旅行安排。
如果天气条件不适合某些户外活动，请降低相关活动强度或安排替代方案。

知识库约束：

知识库中的内容是本系统提供的旅行参考资料。

生成旅行计划时必须遵守：

1. 优先利用知识库中的相关信息。
2. 如果知识库包含目的地、季节、活动建议等信息，应优先采用。
3. 如果知识库没有覆盖的信息，可以使用通用旅行知识补充。
4. 不得声称不存在于知识库中的内容来自知识库。
5. 不得编造具体事实，例如不存在的景点、路线、价格、天气数据。

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