from app.schemas import TripPlan
from app.services.version_compare import compare_trip_plans


def test_compare_trip_plans():
    old_plan = TripPlan.model_validate({
        "destination": "Reykjavik",
        "days": [
            {
                "day": 1,
                "title": "雷克雅未克城市探索",
                "activities": [
                    "参观哈尔格林姆斯教堂",
                    "城市摄影",
                    "海边散步"
                ]
            },
            {
                "day": 2,
                "title": "户外徒步",
                "activities": [
                    "山区徒步",
                    "瀑布摄影"
                ]
            }
        ]
    })

    new_plan = TripPlan.model_validate({
        "destination": "Reykjavik",
        "days": [
            {
                "day": 1,
                "title": "雷克雅未克城市探索",
                "activities": [
                    "参观哈尔格林姆斯教堂",
                    "城市摄影",
                    "参观博物馆"
                ]
            },
            {
                "day": 2,
                "title": "恶劣天气室内活动",
                "activities": [
                    "参观国家博物馆",
                    "咖啡馆休息"
                ]
            }
        ]
    })

    result = compare_trip_plans(
        old_plan=old_plan,
        new_plan=new_plan
    )

    assert result["destination"] == "Reykjavik"
    assert result["total_days"] == 2
    assert result["changed_days"] == 2

    day1 = result["days"][0]

    assert day1["status"] == "changed"
    assert "参观哈尔格林姆斯教堂" in day1["kept"]
    assert "城市摄影" in day1["kept"]
    assert "海边散步" in day1["removed"]
    assert "参观博物馆" in day1["added"]

    day2 = result["days"][1]

    assert day2["status"] == "changed"
    assert "山区徒步" in day2["removed"]
    assert "瀑布摄影" in day2["removed"]
    assert "参观国家博物馆" in day2["added"]
    assert "咖啡馆休息" in day2["added"]


def test_unchanged_trip_plan():
    plan = TripPlan.model_validate({
        "destination": "Reykjavik",
        "days": [
            {
                "day": 1,
                "title": "城市探索",
                "activities": [
                    "城市摄影",
                    "参观博物馆"
                ]
            }
        ]
    })

    result = compare_trip_plans(
        old_plan=plan,
        new_plan=plan
    )

    assert result["changed_days"] == 0
    assert result["days"][0]["status"] == "unchanged"
    assert "城市摄影" in result["days"][0]["kept"]
    assert "参观博物馆" in result["days"][0]["kept"]
    assert result["days"][0]["removed"] == []
    assert result["days"][0]["added"] == []