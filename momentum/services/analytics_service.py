"""Aggregation helpers for the Analytics view."""

from __future__ import annotations

from datetime import date, timedelta

from momentum.models.database import Database


class AnalyticsService:
    def __init__(self, db: Database):
        self.db = db

    def get_overview(self) -> dict:
        courses = self.db.get_all_courses()
        total_lessons = sum(c.total_lessons for c in courses)
        completed_lessons = sum(c.completed_lessons for c in courses)
        progress_pct = (completed_lessons / total_lessons * 100.0) if total_lessons > 0 else 0.0
        return {
            "total_courses": len(courses),
            "total_hours": self.db.get_total_watch_time_seconds() / 3600,
            "streak": self.db.get_streak(),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "overall_progress_pct": progress_pct,
            "weekly_watch_seconds": self.db.get_weekly_watch_time_seconds(),
            "streak_time_seconds": self.db.get_streak_time_seconds(),
        }

    def get_weekly_data(self) -> list[tuple[str, int]]:
        """Return (day_label, minutes) for the last 7 days, oldest first."""
        activities = self.db.get_daily_activity(days=7)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        activity_map = {a.date: a.total_seconds for a in activities}
        today = date.today()
        result: list[tuple[str, int]] = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            label = day_names[d.weekday()]
            minutes = activity_map.get(d.isoformat(), 0) // 60
            result.append((label, minutes))
        return result
