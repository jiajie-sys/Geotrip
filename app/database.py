import sqlite3
from pathlib import Path
import json

DATABASE_PATH = Path("data/geotrip.db")


def init_database():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            days INTEGER NOT NULL,
            budget REAL NOT NULL,
            transport TEXT NOT NULL,
            interests TEXT NOT NULL,
            travel_month INTEGER NOT NULL,
            plan_json TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()

def save_trip(request, plan):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO trips (
            destination,
            days,
            budget,
            transport,
            interests,
            travel_month,
            plan_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.destination,
            request.days,
            request.budget,
            request.transport,
            json.dumps(request.interests, ensure_ascii=False),
            request.travel_month,
            plan.model_dump_json()
        )
    )

    trip_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return trip_id

def get_trip(trip_id: int):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trips
        WHERE id = ?
        """,
        (trip_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "trip_id": row["id"],
        "destination": row["destination"],
        "days": row["days"],
        "budget": row["budget"],
        "transport": row["transport"],
        "interests": json.loads(row["interests"]),
        "travel_month": row["travel_month"],
        "plan": json.loads(row["plan_json"])
    }
def delete_trip(trip_id: int):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM trips
        WHERE id = ?
        """,
        (trip_id,)
    )

    deleted_count = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted_count > 0
def update_trip_budget(trip_id: int, new_budget: float):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE trips
        SET budget = ?
        WHERE id = ?
        """,
        (new_budget, trip_id)
    )

    updated_count = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_count > 0