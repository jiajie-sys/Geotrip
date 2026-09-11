from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.schemas import (
    TripRequest,
    TripPlan,
    BudgetUpdate,
    ReplanRequest
)

from app.services.planner import create_trip_plan
from app.services.replanner import replan_trip
from app.services.version_compare import compare_trip_plans

from app.database import (
    init_database,
    get_trip,
    delete_trip,
    update_trip_budget,
    get_trip_versions,
    get_trip_version
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="GeoTrip",
    description="AI-powered travel planning assistant",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "GeoTrip API is running"
    }


@app.post("/api/v1/trips/plan")
def plan_trip(
    request: TripRequest
):
    return create_trip_plan(
        request
    )


@app.get("/api/v1/trips/{trip_id}")
def read_trip(
    trip_id: int
):
    trip = get_trip(
        trip_id
    )

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    return trip


@app.delete("/api/v1/trips/{trip_id}")
def remove_trip(
    trip_id: int
):
    deleted = delete_trip(
        trip_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    return {
        "message": "旅行计划已删除"
    }


@app.patch("/api/v1/trips/{trip_id}/budget")
def change_trip_budget(
    trip_id: int,
    request: BudgetUpdate
):
    updated = update_trip_budget(
        trip_id=trip_id,
        budget=request.budget
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    return {
        "message": "预算更新成功",
        "trip_id": trip_id,
        "budget": request.budget
    }


@app.post("/api/v1/trips/{trip_id}/replan")
def replan_existing_trip(
    trip_id: int,
    request: ReplanRequest
):
    trip = get_trip(
        trip_id
    )

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    if not trip.get("start_date"):
        raise HTTPException(
            status_code=400,
            detail=(
                "该旅行计划是旧数据，"
                "没有 start_date，"
                "请重新创建旅行计划"
            )
        )

    original_request = TripRequest(
        destination=trip["destination"],
        days=trip["days"],
        budget=trip["budget"],
        transport=trip["transport"],
        interests=trip["interests"],
        travel_month=trip["travel_month"],
        start_date=trip["start_date"]
    )

    original_plan = TripPlan.model_validate(
        trip["plan"]
    )

    weather = request.model_dump()

    result = replan_trip(
        trip_id=trip_id,
        request=original_request,
        original_plan=original_plan,
        weather=weather
    )

    return result


@app.get(
    "/api/v1/trips/{trip_id}/versions"
)
def list_trip_versions(
    trip_id: int
):
    trip = get_trip(
        trip_id
    )

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    versions = get_trip_versions(
        trip_id
    )

    return {
        "trip_id": trip_id,
        "versions": versions
    }


@app.get(
    "/api/v1/trips/{trip_id}/versions/compare"
)
def compare_trip_versions(
    trip_id: int,
    from_version: int,
    to_version: int
):
    trip = get_trip(
        trip_id
    )

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    if from_version <= 0:
        raise HTTPException(
            status_code=400,
            detail="from_version 必须大于 0"
        )

    if to_version <= 0:
        raise HTTPException(
            status_code=400,
            detail="to_version 必须大于 0"
        )

    if from_version == to_version:
        raise HTTPException(
            status_code=400,
            detail="不能比较同一个版本"
        )

    old_version = get_trip_version(
        trip_id=trip_id,
        version=from_version
    )

    if old_version is None:
        raise HTTPException(
            status_code=404,
            detail=f"版本 V{from_version} 不存在"
        )

    new_version = get_trip_version(
        trip_id=trip_id,
        version=to_version
    )

    if new_version is None:
        raise HTTPException(
            status_code=404,
            detail=f"版本 V{to_version} 不存在"
        )

    old_plan = TripPlan.model_validate(
        old_version["plan"]
    )

    new_plan = TripPlan.model_validate(
        new_version["plan"]
    )

    comparison = compare_trip_plans(
        old_plan=old_plan,
        new_plan=new_plan
    )

    return {
        "trip_id": trip_id,
        "from_version": from_version,
        "to_version": to_version,
        "from_reason": old_version["reason"],
        "to_reason": new_version["reason"],
        "to_risk": new_version["risk"],
        "comparison": comparison
    }


@app.get(
    "/api/v1/trips/{trip_id}/versions/{version}"
)
def read_trip_version(
    trip_id: int,
    version: int
):
    trip = get_trip(
        trip_id
    )

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="旅行计划不存在"
        )

    result = get_trip_version(
        trip_id=trip_id,
        version=version
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="该版本不存在"
        )

    return result