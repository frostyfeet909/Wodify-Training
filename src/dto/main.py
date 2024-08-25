"""Data transfer objects for the main module."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import time as time_type


class RawWorkout(TypedDict):
    """Raw workout data."""

    workout: str
    time: str
    duration: str
    coach: str
    status: str
    date: str

class CleanWorkout(TypedDict):
    """Clean workout data."""

    workout: str
    time: "time_type"
    duration: int
    coach: str
    year: int
    month: int
    day: str
    capacity: int
    attendance: int
    overflow: int
