"""Scrape the workout data from the HTML files."""
import re
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from pandas import DataFrame

from src import dto


def get_data() -> Generator[str, None, None]:
    """Get the HTML data from the calendar files."""
    data_dir = Path(__file__).parent.parent/ "data" / "calendar"
    for file in data_dir.iterdir():
        with file.open() as f:
            yield f.read()


def scrape_data(html: str) -> list[dto.RawWorkout]:
    """Scrape the workout data from the HTML."""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find("tbody").find_all("tr")  # type: ignore[reportAttributeAccessIssue]
    current_day = None

    workouts = []
    for row in rows:
        if row.get("style", "") == "":
            current_day = row.find("span", class_="h3").get_text(strip=True)
            continue

        details = {}
        columns = row.find_all("td", class_="TableRecords_OddLine") + row.find_all(
            "td", class_="TableRecords_EvenLine"
        )

        if columns:
            details["workout"] = columns[4].get_text(strip=True)
            details["time"] = columns[6].get_text(strip=True)
            details["duration"] = columns[7].get_text(strip=True)
            details["coach"] = columns[8].get_text(strip=True)
            details["status"] = columns[1].get_text(strip=True)
            details["date"] = current_day

        if details:
            workouts.append(details)

    return workouts

def clean_data(workouts: list[dto.RawWorkout]) -> list[dto.CleanWorkout]:
    """
    Clean the workout data.

    Transforms the raw workout data into a clean format.
    """
    clean_workouts: list[dto.CleanWorkout] = []
    for workout in workouts:
        if workout["status"] == "CANCELLED":
            continue
        day, date_part_1, date_part_2 = re.split(r'(\d+)', workout["date"], maxsplit=1)
        date = datetime.strptime(date_part_1 + date_part_2, "%d-%m-%Y").date()  # noqa: DTZ007 - No timezone in raw data.
        numbers = re.findall(r'\d+', workout["status"])
        clean_workout: dto.CleanWorkout = {
            "workout": workout["workout"],
            "time": datetime.strptime(workout["time"], "%I:%M %p").time(),  # noqa: DTZ007 - No timezone in raw data.
            "duration": int(workout["duration"].removesuffix("'")),
            "year": date.year,
            "month": date.month,
            "day": day,
            "coach": workout["coach"],
            "capacity": int(numbers[1]),
            "attendance": int(numbers[0]),
            "overflow": int(numbers[2]) if len(numbers) > 2 else 0,  # noqa: PLR2004 - Don't need this for scapring.
        }
        clean_workouts.append(clean_workout)

    return clean_workouts


def store_data(workouts: list[dto.CleanWorkout]) -> None:
    """
    Store the workout data.

    Stores the workout data in a pickle and CSV file.
    """
    data_dir = Path(__file__).parent.parent/ "data"
    workouts_df = DataFrame(workouts)
    workouts_df.to_pickle(data_dir / "workouts.pkl")
    workouts_df.to_csv(data_dir / "workouts.csv", index=False)

def main() -> None:
    """Scrape and store the workout data."""
    workouts: list[dto.CleanWorkout] = []
    for data in get_data():
        workouts.extend(clean_data(workouts=scrape_data(html=data)))

    store_data(workouts=workouts)

if __name__ == "__main__":
    main()
