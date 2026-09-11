import os
import json
import logging

from dotenv import load_dotenv
from openai import OpenAI, APIError
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import TripRequest, TripPlan
from app.prompts import build_trip_prompt
from app.database import save_trip
from app.rag.faiss_store import retrieve_faiss_context
from app.tools.weather import (
    get_city_weather,
    should_use_weather_tool
)


load_dotenv()

logger = logging.getLogger(__name__)


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def build_rag_query(request: TripRequest):
    return f"""
    {request.travel_month}月份去{request.destination}旅行，
    出发日期是{request.start_date.isoformat()}，
    交通方式是{request.transport}，
    兴趣包括{", ".join(request.interests)}，
    预算是{request.budget}元。
    """


def get_weather_context(request: TripRequest):
    if not should_use_weather_tool(
        request.start_date
    ):
        logger.info(
            "Trip date %s is outside weather forecast range.",
            request.start_date
        )

        return ""

    try:
        weather = get_city_weather(
            city=request.destination,
            target_date=request.start_date
        )

        logger.info(
            "Weather result: %s",
            weather
        )

        return json.dumps(
            weather,
            ensure_ascii=False,
            indent=2
        )

    except Exception as error:
        logger.warning(
            "Weather tool failed: %s",
            error
        )

        return ""


def create_trip_plan(
    request: TripRequest
):
    feedback = ""

    rag_query = build_rag_query(
        request
    )

    logger.info(
        "RAG query: %s",
        rag_query
    )

    try:
        context = retrieve_faiss_context(
            query=rag_query,
            top_k=2
        )

    except Exception as error:
        logger.exception(
            "FAISS retrieval failed"
        )

        context = ""

    logger.info(
        "RAG context: %s",
        context
    )

    weather_context = (
        get_weather_context(
            request
        )
    )

    logger.info(
        "Weather context: %s",
        weather_context
    )

    for attempt in range(2):
        prompt = build_trip_prompt(
            request=request,
            context=context,
            weather_context=weather_context,
            feedback=feedback
        )

        try:
            response = (
                client
                .chat
                .completions
                .create(
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7
                )
            )

            raw_content = (
                response
                .choices[0]
                .message
                .content
            )

            logger.info(
                "LLM response attempt %s: %s",
                attempt + 1,
                raw_content
            )

            data = json.loads(
                raw_content
            )

            plan = TripPlan.model_validate(
                data
            )

            if len(plan.days) != request.days:
                feedback = f"""
上一次生成的行程天数不正确。

用户要求：
{request.days} 天

你实际生成：
{len(plan.days)} 天

请重新生成。

必须严格生成 {request.days} 天行程，
不得多于或少于该天数。
"""

                continue

            trip_id = save_trip(
                request=request,
                plan=plan
            )

            return {
                "trip_id": trip_id,
                "plan": plan
            }

        except APIError as error:
            logger.exception(
                "DeepSeek API error"
            )

            raise HTTPException(
                status_code=502,
                detail=(
                    "DeepSeek API 调用失败："
                    f"{str(error)}"
                )
            )

        except json.JSONDecodeError:
            logger.warning(
                "LLM returned invalid JSON "
                "on attempt %s",
                attempt + 1
            )

            feedback = """
上一次输出不是合法 JSON。

请重新生成。

不要使用 Markdown 代码块。
不要添加 ```json。
不要输出任何解释。
只能返回合法 JSON。
"""

        except ValidationError as error:
            logger.warning(
                "TripPlan validation failed "
                "on attempt %s: %s",
                attempt + 1,
                error
            )

            feedback = """
上一次返回的数据结构不符合要求。

请严格按照指定 JSON 格式重新生成。

必须包含：

destination
days

days 中每一项必须包含：

day
title
activities
"""

        except Exception as error:
            logger.exception(
                "Unexpected planner error"
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "旅行计划生成失败："
                    f"{str(error)}"
                )
            )

    raise HTTPException(
        status_code=502,
        detail=(
            "AI 连续两次生成了"
            "无效的旅行计划"
        )
    )