import uuid
from typing import List
import datetime
from models.location import Location
from models.reports import Report

__reports: List[Report] = []
# fake db


async def get_reports() -> List[Report]:
    return list(__reports)


async def add_report(description: str, location: Location) -> Report:
    now = datetime.datetime.now()
    report = Report(id=str(uuid.uuid4()),
                    location=location,
                    description=description,
                    created_date=now)
    # if using real db use async calls

    __reports.append(report)
    __reports.sort(key=lambda r: r.created_date, reverse=True)
    return report
