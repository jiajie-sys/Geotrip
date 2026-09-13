import os
import requests
import streamlit as st
from datetime import date


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000/api/v1"
)


st.set_page_config(
    page_title="GeoTrip",
    page_icon="🌍",
    layout="wide"
)


def generate_trip(
    destination,
    start_date,
    days,
    budget,
    transport,
    interests
):
    payload = {
        "destination": destination,
        "days": int(days),
        "budget": float(budget),
        "transport": transport,
        "interests": interests,
        "travel_month": start_date.month,
        "start_date": start_date.isoformat()
    }

    response = requests.post(
        f"{API_BASE_URL}/trips/plan",
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()


def replan_trip(
    trip_id,
    precipitation_probability,
    wind_speed_max,
    temperature_min,
    temperature_max
):
    payload = {
        "precipitation_probability": float(
            precipitation_probability
        ),
        "wind_speed_max": float(
            wind_speed_max
        ),
        "temperature_min": float(
            temperature_min
        ),
        "temperature_max": float(
            temperature_max
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/trips/{trip_id}/replan",
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()


def compare_versions(
    trip_id,
    from_version,
    to_version
):
    response = requests.get(
        f"{API_BASE_URL}/trips/{trip_id}/versions/compare",
        params={
            "from_version": from_version,
            "to_version": to_version
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def show_plan(plan, title=None):
    if title:
        st.subheader(title)

    st.markdown(
        f"### 📍 {plan['destination']}"
    )

    for day_plan in plan["days"]:
        with st.container(border=True):
            st.markdown(
                f"### Day {day_plan['day']} · "
                f"{day_plan['title']}"
            )

            for activity in day_plan["activities"]:
                st.markdown(
                    f"- {activity}"
                )


def show_version_comparison(result):
    comparison = result["comparison"]

    st.subheader("🔍 V1 → V2 行程变化")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "原版本",
            f"V{result['from_version']}"
        )

    with col2:
        st.metric(
            "新版本",
            f"V{result['to_version']}"
        )

    with col3:
        st.metric(
            "发生变化的天数",
            comparison["changed_days"]
        )

    st.caption(
        f"{result['from_reason']} → "
        f"{result['to_reason']}"
    )

    for day in comparison["days"]:
        status = day["status"]

        if status == "unchanged":
            status_text = "未变化"
            status_icon = "✅"

        elif status == "changed":
            status_text = "已调整"
            status_icon = "🔄"

        elif status == "added_day":
            status_text = "新增"
            status_icon = "➕"

        elif status == "removed_day":
            status_text = "删除"
            status_icon = "❌"

        else:
            status_text = status
            status_icon = "ℹ️"

        with st.expander(
            f"{status_icon} Day {day['day']} · {status_text}",
            expanded=(status != "unchanged")
        ):
            if day["old_title"]:
                st.markdown(
                    f"**原标题：** {day['old_title']}"
                )

            if day["new_title"]:
                st.markdown(
                    f"**新标题：** {day['new_title']}"
                )

            if day["kept"]:
                st.markdown("#### ✅ 保留活动")

                for activity in day["kept"]:
                    st.markdown(
                        f"- {activity}"
                    )

            if day["removed"]:
                st.markdown("#### ❌ 删除活动")

                for activity in day["removed"]:
                    st.markdown(
                        f"- {activity}"
                    )

            if day["added"]:
                st.markdown("#### ➕ 新增活动")

                for activity in day["added"]:
                    st.markdown(
                        f"- {activity}"
                    )

            if (
                not day["kept"]
                and not day["removed"]
                and not day["added"]
            ):
                st.info(
                    "该天的活动内容没有发生变化。"
                )


st.title("🌍 GeoTrip")
st.caption("AI 户外旅行规划助手")

st.markdown(
    """
输入你的旅行需求，GeoTrip 将结合旅行知识库、
AI 与天气信息，为你生成个性化旅行计划。
"""
)


with st.sidebar:
    st.header("✈️ 旅行需求")

    destination = st.text_input(
        "目的地",
        value="Reykjavik"
    )

    start_date = st.date_input(
        "出发日期",
        value=date.today()
    )

    days = st.number_input(
        "旅行天数",
        min_value=1,
        max_value=30,
        value=3
    )

    budget = st.number_input(
        "预算（人民币）",
        min_value=100.0,
        value=8000.0,
        step=500.0
    )

    transport = st.selectbox(
        "交通方式",
        [
            "car",
            "public transport",
            "walking",
            "mixed"
        ]
    )

    interests = st.multiselect(
        "旅行兴趣",
        [
            "hiking",
            "photography",
            "nature",
            "food",
            "culture",
            "history",
            "city walk"
        ],
        default=[
            "hiking",
            "photography"
        ]
    )

    generate_button = st.button(
        "✨ AI 生成行程",
        use_container_width=True
    )


if generate_button:
    if not destination.strip():
        st.warning(
            "请输入目的地。"
        )

    elif not interests:
        st.warning(
            "请至少选择一个旅行兴趣。"
        )

    else:
        try:
            with st.spinner(
                "GeoTrip 正在检索知识、查询天气并生成行程..."
            ):
                result = generate_trip(
                    destination=destination,
                    start_date=start_date,
                    days=days,
                    budget=budget,
                    transport=transport,
                    interests=interests
                )

            st.session_state[
                "trip_result"
            ] = result

            st.session_state.pop(
                "replan_result",
                None
            )

            st.session_state.pop(
                "compare_result",
                None
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "无法连接 GeoTrip 后端，请确认 FastAPI 已启动。"
            )

        except requests.exceptions.Timeout:
            st.error(
                "AI 生成时间过长，请稍后重试。"
            )

        except requests.exceptions.HTTPError as error:
            st.error(
                f"后端返回错误：{error}"
            )

        except Exception as error:
            st.error(
                f"发生未知错误：{error}"
            )


if "trip_result" not in st.session_state:
    st.info(
        "👈 在左侧填写旅行需求，然后点击「AI 生成行程」。"
    )

else:
    trip_result = st.session_state[
        "trip_result"
    ]

    trip_id = trip_result["trip_id"]

    st.success(
        f"旅行计划生成成功 · Trip ID #{trip_id}"
    )

    show_plan(
        plan=trip_result["plan"],
        title="🗺️ V1 · 原始旅行计划"
    )

    st.divider()

    st.header(
        "🌦️ 天气风险与动态重规划"
    )

    st.caption(
        "GeoTrip 在生成 V1 行程时已结合目的地、"
        "出发日期与天气信息进行规划。"
        "当旅行期间天气发生明显变化时，"
        "系统可以重新评估风险并生成新的旅行方案。"
    )

    st.info(
        f"📍 {destination} · "
        f"{start_date.strftime('%Y/%m/%d')}  "
        "当前 V1 已结合天气信息生成。"
    )

    with st.expander(
        "🧪 Demo · 模拟极端天气变化",
        expanded=False
    ):
        st.caption(
            "用于模拟旅行计划生成后天气突然恶化的情况，"
            "验证 GeoTrip 的天气风险评估与动态重规划能力。"
        )

        col1, col2 = st.columns(2)

        with col1:
            precipitation_probability = st.slider(
                "🌧️ 降水概率 (%)",
                min_value=0,
                max_value=100,
                value=90
            )

            temperature_min = st.number_input(
                "🥶 最低温度 (°C)",
                value=-2.0,
                step=1.0
            )

        with col2:
            wind_speed_max = st.number_input(
                "💨 最大风速 (km/h)",
                min_value=0.0,
                value=65.0,
                step=5.0
            )

            temperature_max = st.number_input(
                "🌡️ 最高温度 (°C)",
                value=5.0,
                step=1.0
            )

        replan_button = st.button(
            "⚠️ 模拟天气突变并重新规划",
            type="primary",
            use_container_width=True
        )

    if replan_button:
        try:
            with st.spinner(
                "GeoTrip 正在评估天气风险并重新规划..."
            ):
                replan_result = replan_trip(
                    trip_id=trip_id,
                    precipitation_probability=(
                        precipitation_probability
                    ),
                    wind_speed_max=wind_speed_max,
                    temperature_min=temperature_min,
                    temperature_max=temperature_max
                )

            st.session_state[
                "replan_result"
            ] = replan_result

            st.session_state.pop(
                "compare_result",
                None
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "无法连接 GeoTrip 后端。"
            )

        except requests.exceptions.Timeout:
            st.error(
                "动态重新规划时间过长，请稍后重试。"
            )

        except requests.exceptions.HTTPError as error:
            st.error(
                f"重新规划失败：{error}"
            )

        except Exception as error:
            st.error(
                f"发生未知错误：{error}"
            )


    if "replan_result" in st.session_state:
        replan_result = st.session_state[
            "replan_result"
        ]

        risk = replan_result["risk"]

        st.divider()

        st.subheader(
            "⚠️ 天气风险评估"
        )

        risk_level = risk["level"]

        if risk_level == "high":
            st.error(
                f"高风险 · Risk Score {risk['score']}"
            )

        elif risk_level == "medium":
            st.warning(
                f"中等风险 · Risk Score {risk['score']}"
            )

        else:
            st.success(
                f"低风险 · Risk Score {risk['score']}"
            )

        if risk["reasons"]:
            for reason in risk["reasons"]:
                st.markdown(
                    f"- {reason}"
                )

        else:
            st.markdown(
                "- 当前没有检测到明显天气风险。"
            )

        if replan_result["replanned"]:
            version = replan_result[
                "version"
            ]

            st.success(
                f"GeoTrip 已重新规划，"
                f"生成 V{version}。"
            )

            show_plan(
                plan=replan_result["plan"],
                title=(
                    f"🔄 V{version} · "
                    "天气调整后的旅行计划"
                )
            )

            st.divider()

            compare_button = st.button(
                "🔍 查看 V1 → V2 变化",
                use_container_width=True
            )

            if compare_button:
                try:
                    with st.spinner(
                        "GeoTrip 正在比较两个版本..."
                    ):
                        compare_result = (
                            compare_versions(
                                trip_id=trip_id,
                                from_version=1,
                                to_version=version
                            )
                        )

                    st.session_state[
                        "compare_result"
                    ] = compare_result

                except requests.exceptions.HTTPError as error:
                    st.error(
                        f"版本比较失败：{error}"
                    )

                except Exception as error:
                    st.error(
                        f"发生未知错误：{error}"
                    )

        else:
            st.info(
                "当前天气风险不足以触发重新规划，"
                "继续使用原始旅行计划。"
            )


    if "compare_result" in st.session_state:
        st.divider()

        show_version_comparison(
            st.session_state[
                "compare_result"
            ]
        )