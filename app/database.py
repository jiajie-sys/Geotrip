import json
import sqlite3
from pathlib import Path

from app.schemas import TripRequest, TripPlan


DATABASE_PATH = Path("data/geotrip.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            days INTEGER NOT NULL,
            budget REAL NOT NULL,
            transport TEXT NOT NULL,
            interests TEXT NOT NULL,
            travel_month INTEGER NOT NULL,
            start_date TEXT,
            plan_json TEXT NOT NULL
        )
    """)

    cursor.execute(
        "PRAGMA table_info(trips)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "start_date" not in columns:
        cursor.execute("""
            ALTER TABLE trips
            ADD COLUMN start_date TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trip_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            reason TEXT,
            risk_json TEXT,
            plan_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        )
    """)

    connection.commit()
    connection.close()


def save_trip(
    request: TripRequest,
    plan: TripPlan
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO trips (
                destination,
                days,
                budget,
                transport,
                interests,
                travel_month,
                start_date,
                plan_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.destination,
                request.days,
                request.budget,
                request.transport,
                json.dumps(
                    request.interests,
                    ensure_ascii=False
                ),
                request.travel_month,
                request.start_date.isoformat(),
                plan.model_dump_json()
            )
        )

        trip_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO trip_versions (
                trip_id,
                version,
                reason,
                risk_json,
                plan_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                trip_id,
                1,
                "original_plan",
                None,
                plan.model_dump_json()
            )
        )

        connection.commit()

        return trip_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_trip(
    trip_id: int
):
    connection = get_connection()
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
        "id": row["id"],
        "destination": row["destination"],
        "days": row["days"],
        "budget": row["budget"],
        "transport": row["transport"],
        "interests": json.loads(
            row["interests"]
        ),
        "travel_month": row["travel_month"],
        "start_date": row["start_date"],
        "plan": json.loads(
            row["plan_json"]
        )
    }


def delete_trip(
    trip_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM trips
        WHERE id = ?
        """,
        (trip_id,)
    )

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


def update_trip_budget(
    trip_id: int,
    budget: float
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE trips
        SET budget = ?
        WHERE id = ?
        """,
        (
            budget,
            trip_id
        )
    )

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


def save_trip_version(
    trip_id: int,
    plan: TripPlan,
    risk: dict | None = None,
    reason: str = ""
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT MAX(version)
            FROM trip_versions
            WHERE trip_id = ?
            """,
            (trip_id,)
        )

        row = cursor.fetchone()

        current_version = (
            row[0]
            if row[0] is not None
            else 0
        )

        new_version = (
            current_version + 1
        )

        cursor.execute(
            """
            INSERT INTO trip_versions (
                trip_id,
                version,
                reason,
                risk_json,
                plan_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                trip_id,
                new_version,
                reason,
                (
                    json.dumps(
                        risk,
                        ensure_ascii=False
                    )
                    if risk
                    else None
                ),
                plan.model_dump_json()
            )
        )

        connection.commit()

        return new_version

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_trip_versions(
    trip_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trip_versions
        WHERE trip_id = ?
        ORDER BY version ASC
        """,
        (trip_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:
        results.append({
            "id": row["id"],
            "trip_id": row["trip_id"],
            "version": row["version"],
            "reason": row["reason"],
            "risk": (
                json.loads(
                    row["risk_json"]
                )
                if row["risk_json"]
                else None
            ),
            "plan": json.loads(
                row["plan_json"]
            ),
            "created_at": row["created_at"]
        })

    return results


def get_trip_version(
    trip_id: int,
    version: int
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trip_versions
        WHERE trip_id = ?
        AND version = ?
        """,
        (
            trip_id,
            version
        )
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "trip_id": row["trip_id"],
        "version": row["version"],
        "reason": row["reason"],
        "risk": (
            json.loads(
                row["risk_json"]
            )
            if row["risk_json"]
            else None
        ),
        "plan": json.loads(
            row["plan_json"]
        ),
        "created_at": row["created_at"]
    }