from pydantic import BaseModel, Field
from typing import List
from datetime import date

class TripRequest(BaseModel):
    destination: str
    days: int
    budget: float
    transport: str
    interests: List[str]
    travel_month: int = Field(ge=1, le=12)
    start_date: date

class DayPlan(BaseModel):
    day: int
    title: str
    activities: List[str]


class TripPlan(BaseModel):
    destination: str
    days: List[DayPlan]


class BudgetUpdate(BaseModel):
    budget: float = Field(gt=0)

class ReplanRequest(BaseModel):
    precipitation_probability: float = Field(ge=0, le=100)
    wind_speed_max: float = Field(ge=0)
    temperature_min: float
    temperature_max: float