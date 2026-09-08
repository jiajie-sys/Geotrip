import os
import json

from dotenv import load_dotenv
from openai import OpenAI, APIError
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import TripRequest, TripPlan


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def create_trip_plan(request: TripRequest):
    feedback = ""

    for attempt in range(2):
        prompt = f"""
你是 GeoTrip 的旅行规划助手。

请根据以下信息生成旅行计划：

目的地：{request.destination}
旅行天数：{request.days}
预算：{request.budget} 元
交通方式：{request.transport}
兴趣：{", ".join(request.interests)}
旅行月份：{request.travel_month}

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

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are GeoTrip, an AI travel planning assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            plan_text = response.choices[0].message.content
            plan_data = json.loads(plan_text)

            plan = TripPlan.model_validate(plan_data)

            if len(plan.days) == request.days:
                return plan

            feedback = (
                f"你上一次生成了 {len(plan.days)} 天行程，"
                f"但用户要求 {request.days} 天。"
                f"请重新生成，并严格生成 {request.days} 天。"
            )

        except APIError:
            raise HTTPException(
                status_code=502,
                detail="DeepSeek API request failed"
            )

        except json.JSONDecodeError:
            feedback = (
                "你上一次返回的内容不是合法 JSON。"
                "请重新生成，并且只返回合法 JSON。"
            )

        except ValidationError:
            feedback = (
                "你上一次返回的 JSON 结构不符合要求。"
                "请严格按照指定的 destination 和 days 结构重新生成。"
            )

    raise HTTPException(
        status_code=502,
        detail="AI failed to generate a valid trip plan after retry"
    )