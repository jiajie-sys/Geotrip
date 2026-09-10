import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.database import init_database, get_trip, delete_trip, update_trip_budget
from app.schemas import TripRequest, BudgetUpdate
from app.services.planner import create_trip_plan


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="GeoTrip API",
    description="AI-powered travel planning assistant",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "GeoTrip API is running"
    }


@app.post("/api/v1/trips/plan")
def plan_trip(request: TripRequest):
    return create_trip_plan(request)


@app.get("/api/v1/trips/{trip_id}")
def read_trip(trip_id: int):
    trip = get_trip(trip_id)

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip

@app.delete("/api/v1/trips/{trip_id}")
def remove_trip(trip_id: int):
    deleted = delete_trip(trip_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return {
        "message": "Trip deleted successfully"
    }
@app.patch("/api/v1/trips/{trip_id}/budget")
def change_trip_budget(trip_id: int, request: BudgetUpdate):
    updated = update_trip_budget(
        trip_id,
        request.budget
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return get_trip(trip_id)