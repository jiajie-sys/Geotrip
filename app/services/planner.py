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
from app.rag.retriever import retrieve_context


load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def create_trip_plan(request: TripRequest):
    feedback = ""

    query = f"""
    {request.travel_month}月份去{request.destination}旅行，
    交通方式是{request.transport}，
    兴趣包括{", ".join(request.interests)}，
    预算是{request.budget}元。
    """

    context = retrieve_context(
        query=query,
        top_k=2
    )

    logger.info("RAG query: %s", query)
    logger.info("RAG context: %s", context)

    for attempt in range(2):
        prompt = build_trip_prompt(
            request=request,
            context=context,
            feedback=feedback
        )

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            raw_content = response.choices[0].message.content

            logger.info(
                "LLM response attempt %s: %s",
                attempt + 1,
                raw_content
            )

            data = json.loads(raw_content)

            plan = TripPlan.model_validate(data)

            if len(plan.days) != request.days:
                feedback = f"""
上一次生成的行程天数不正确。
用户要求 {request.days} 天，
但你生成了 {len(plan.days)} 天。

请重新生成，并严格返回 {request.days} 天。
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
            logger.exception("DeepSeek API error")

            raise HTTPException(
                status_code=502,
                detail=f"DeepSeek API 调用失败: {str(error)}"
            )

        except json.JSONDecodeError:
            logger.warning(
                "LLM returned invalid JSON on attempt %s",
                attempt + 1
            )

            feedback = """
上一次输出不是合法 JSON。
请重新生成。
不要使用 Markdown 代码块。
不要输出任何解释，只返回合法 JSON。
"""

        except ValidationError as error:
            logger.warning(
                "TripPlan validation failed on attempt %s: %s",
                attempt + 1,
                error
            )

            feedback = """
上一次返回的数据结构不符合要求。

请严格按照指定 JSON 格式重新生成。
必须包含 destination 和 days。
days 中每一项必须包含 day、title 和 activities。
"""

    raise HTTPException(
        status_code=502,
        detail="AI 连续两次生成了无效的旅行计划"
    )