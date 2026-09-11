import json
import logging

from fastapi import HTTPException
from openai import APIError
from pydantic import ValidationError

from app.schemas import TripRequest, TripPlan
from app.prompts import build_trip_prompt
from app.services.planner import client
from app.rag.faiss_store import retrieve_faiss_context
from app.tools.weather_risk import evaluate_weather_risk
from app.database import save_trip_version


logger = logging.getLogger(__name__)


def replan_trip(
    trip_id: int,
    request: TripRequest,
    original_plan: TripPlan,
    weather: dict
):
    risk = evaluate_weather_risk(
        weather
    )

    logger.info(
        "Weather risk: %s",
        risk
    )

    if not risk["should_replan"]:
        return {
            "replanned": False,
            "version": None,
            "risk": risk,
            "plan": original_plan
        }

    query = f"""
{request.destination}旅行，
出发日期为{request.start_date.isoformat()}，
兴趣包括{", ".join(request.interests)}，
需要根据恶劣天气重新规划户外活动。
"""

    try:
        context = retrieve_faiss_context(
            query=query,
            top_k=2
        )

    except Exception as error:
        logger.warning(
            "RAG retrieval failed during replanning: %s",
            error
        )

        context = ""

    weather_context = json.dumps(
        weather,
        ensure_ascii=False,
        indent=2
    )

    risk_reasons = "\n".join(
        f"- {reason}"
        for reason in risk["reasons"]
    )

    original_plan_json = json.dumps(
        original_plan.model_dump(),
        ensure_ascii=False,
        indent=2
    )

    feedback = f"""
这是一次天气变化后的动态重新规划。

原始旅行计划如下：

{original_plan_json}

天气风险等级：
{risk["level"]}

天气风险原因：

{risk_reasons}

请根据天气风险重新调整行程。

要求：

1. 尽量保留原计划中仍然安全、合理的活动。
2. 对受恶劣天气影响明显的户外活动进行替换、降级或调整。
3. 不要仅仅增加“注意安全”之类的提示，必须真正调整不合理的活动。
4. 保持旅行总天数不变。
"""

    prompt = build_trip_prompt(
        request=request,
        context=context,
        weather_context=weather_context,
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
            temperature=0.5
        )

        raw_content = (
            response
            .choices[0]
            .message
            .content
        )

        logger.info(
            "Replanned LLM response: %s",
            raw_content
        )

        data = json.loads(
            raw_content
        )

        new_plan = TripPlan.model_validate(
            data
        )

        if len(new_plan.days) != request.days:
            raise HTTPException(
                status_code=502,
                detail="重新规划后的行程天数不正确"
            )

        version = save_trip_version(
            trip_id=trip_id,
            plan=new_plan,
            risk=risk,
            reason="weather_replan"
        )

        return {
            "replanned": True,
            "version": version,
            "risk": risk,
            "plan": new_plan
        }

    except APIError as error:
        logger.exception(
            "DeepSeek API failed during replanning"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                f"动态重新规划失败：{str(error)}"
            )
        )

    except json.JSONDecodeError:
        logger.exception(
            "Replanning returned invalid JSON"
        )

        raise HTTPException(
            status_code=502,
            detail="动态重新规划返回了无效 JSON"
        )

    except ValidationError as error:
        logger.exception(
            "Replanned TripPlan validation failed"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                f"重新规划结果格式错误：{str(error)}"
            )
        )