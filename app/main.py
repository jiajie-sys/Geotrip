from fastapi import FastAPI

from app.schemas import TripRequest
from app.services.planner import create_trip_plan


app = FastAPI(
    title="GeoTrip API",
    description="AI-powered travel planning assistant",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "GeoTrip API is running"
    }


@app.post("/api/v1/trips/plan")
def plan_trip(request: TripRequest):
    return create_trip_plan(request)