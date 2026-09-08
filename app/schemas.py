from pydantic import BaseModel, Field
from typing import List


class TripRequest(BaseModel):
    destination: str
    days: int
    budget: float
    transport: str
    interests: List[str]
    travel_month: int = Field(ge=1, le=12)


class DayPlan(BaseModel):
    day: int
    title: str
    activities: List[str]


class TripPlan(BaseModel):
    destination: str
    days: List[DayPlan]