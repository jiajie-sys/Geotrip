import os
import json

from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.tool_schema import weather_tool
from app.tools.weather import get_city_weather


load_dotenv()


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def main():
    messages = [
        {
            "role": "user",
            "content": (
                "我计划在 2026-09-15 去 Reykjavik 旅行，"
                "请先查询当天的天气预报，"
                "然后根据天气给我一些旅行建议。"
            )
        }
    ]

    print("\n===== 第一次请求 DeepSeek =====")

    first_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[weather_tool],
        tool_choice="auto"
    )

    assistant_message = (
        first_response
        .choices[0]
        .message
    )

    print("\n第一次模型返回：")
    print(assistant_message)

    if not assistant_message.tool_calls:
        print("\n模型没有调用工具。")

        if assistant_message.content:
            print("\n模型直接回答：")
            print(assistant_message.content)

        return

    messages.append(
        assistant_message
    )

    for tool_call in assistant_message.tool_calls:
        function_name = (
            tool_call
            .function
            .name
        )

        raw_arguments = (
            tool_call
            .function
            .arguments
        )

        print("\n===== 模型请求调用工具 =====")

        print("\n工具名称：")
        print(function_name)

        print("\n模型原始参数：")
        print(raw_arguments)

        try:
            arguments = json.loads(
                raw_arguments
            )

        except json.JSONDecodeError as error:
            result = {
                "error": (
                    "模型返回的工具参数不是合法 JSON："
                    f"{str(error)}"
                )
            }

            print("\nJSON 参数解析失败：")
            print(result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False
                )
            })

            continue

        print("\n解析后的参数：")
        print(arguments)

        if function_name == "get_city_weather":
            try:
                city = arguments["city"]

                target_date_string = (
                    arguments["target_date"]
                )

                target_date = (
                    date.fromisoformat(
                        target_date_string
                    )
                )

                print("\nPython 即将执行：")
                print(
                    f"get_city_weather("
                    f"city={city!r}, "
                    f"target_date={target_date}"
                    f")"
                )

                result = get_city_weather(
                    city=city,
                    target_date=target_date
                )

            except KeyError as error:
                result = {
                    "error": (
                        f"缺少工具参数："
                        f"{str(error)}"
                    )
                }

            except ValueError as error:
                result = {
                    "error": str(error)
                }

            except Exception as error:
                result = {
                    "error": (
                        "天气工具执行失败："
                        f"{str(error)}"
                    )
                }

        else:
            result = {
                "error": (
                    f"未知工具："
                    f"{function_name}"
                )
            }

        print("\n===== Python 工具执行结果 =====")
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            )
        )

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(
                result,
                ensure_ascii=False
            )
        })

    print("\n===== 第二次请求 DeepSeek =====")

    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[weather_tool],
        tool_choice="auto"
    )

    final_message = (
        final_response
        .choices[0]
        .message
    )

    print("\nDeepSeek 最终回答：")

    if final_message.content:
        print(
            final_message.content
        )
    else:
        print(
            "模型没有返回最终文本。"
        )

    if final_message.tool_calls:
        print(
            "\n注意：模型第二轮仍然请求调用工具。"
        )

        print(
            final_message.tool_calls
        )


if __name__ == "__main__":
    main()