from app.schemas import TripPlan


def normalize_activity(activity: str):
    return activity.strip().lower()


def compare_day_activities(
    old_activities: list[str],
    new_activities: list[str]
):
    old_map = {
        normalize_activity(activity): activity
        for activity in old_activities
    }

    new_map = {
        normalize_activity(activity): activity
        for activity in new_activities
    }

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())

    kept_keys = old_keys & new_keys
    removed_keys = old_keys - new_keys
    added_keys = new_keys - old_keys

    return {
        "kept": [
            old_map[key]
            for key in kept_keys
        ],
        "removed": [
            old_map[key]
            for key in removed_keys
        ],
        "added": [
            new_map[key]
            for key in added_keys
        ]
    }


def compare_trip_plans(
    old_plan: TripPlan,
    new_plan: TripPlan
):
    old_days = {
        day.day: day
        for day in old_plan.days
    }

    new_days = {
        day.day: day
        for day in new_plan.days
    }

    all_day_numbers = sorted(
        set(old_days.keys())
        | set(new_days.keys())
    )

    day_changes = []

    for day_number in all_day_numbers:
        old_day = old_days.get(
            day_number
        )

        new_day = new_days.get(
            day_number
        )

        if old_day is None:
            day_changes.append({
                "day": day_number,
                "status": "added_day",
                "old_title": None,
                "new_title": new_day.title,
                "kept": [],
                "removed": [],
                "added": new_day.activities
            })

            continue

        if new_day is None:
            day_changes.append({
                "day": day_number,
                "status": "removed_day",
                "old_title": old_day.title,
                "new_title": None,
                "kept": [],
                "removed": old_day.activities,
                "added": []
            })

            continue

        activity_changes = (
            compare_day_activities(
                old_activities=old_day.activities,
                new_activities=new_day.activities
            )
        )

        changed = (
            old_day.title != new_day.title
            or bool(
                activity_changes["removed"]
            )
            or bool(
                activity_changes["added"]
            )
        )

        day_changes.append({
            "day": day_number,
            "status": (
                "changed"
                if changed
                else "unchanged"
            ),
            "old_title": old_day.title,
            "new_title": new_day.title,
            "kept": activity_changes["kept"],
            "removed": activity_changes["removed"],
            "added": activity_changes["added"]
        })

    changed_days = sum(
        1
        for day in day_changes
        if day["status"] != "unchanged"
    )

    return {
        "destination": new_plan.destination,
        "total_days": len(
            new_plan.days
        ),
        "changed_days": changed_days,
        "days": day_changes
    }