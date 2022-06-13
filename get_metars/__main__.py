import asyncio
from datetime import datetime, timedelta
from typing import List
import re
from enum import Enum

import typer

from .database import get_reports

app = typer.Typer()


def remove_spaces(reports: List[str]):
    sanitized_reports: List[str] = []
    for report in reports:
        report = re.sub(r"\s{2,}|\n+|\t+", " ", report)
        report = report.strip()
        sanitized_reports.append(report)
    return sanitized_reports


class ReportType(str, Enum):
    SA = "SA"
    SP = "SP"
    FT = "FT"
    FC = "FC"
    ALL = "ALL"


@app.command()
def main(
    icao: str = typer.Argument(
        default="MROC",
        help="The ICAO code of the station to request, e.g. MROC for Int. Airp. Juan Santamaría",
    ),
    report_type: ReportType = typer.Option(
        default=ReportType.SA,
        help="""Type of report to request.
        SA -> METAR,
        SP -> SPECI,
        FT -> TAF (long),
        FC -> TAF (short),
        ALL -> All types""",
    ),
    init_date: datetime = typer.Option(
        default="2006-01-01T00:00:00",
        help="The initial date to request the reports.",
    ),
    final_date: datetime = typer.Option(
        default=None, help="The final date to request the reports."
    ),
    filename: str = typer.Option(
        default="reports.txt", help="The filename to write the reports on disk."
    ),
    remove_white_spaces: bool = typer.Option(
        default=False,
        is_flag=True,
        help="Remove white spaces of the reports. If True reports will be written in one line.",
    ),
) -> None:
    if report_type == "FT" or report_type == "FC":
        filename = "taf.txt"
    elif report_type == "SA":
        filename = "metar.txt"
    elif filename == "SP":
        filename = "speci.txt"
    else:
        pass

    if final_date is None:
        final_date = init_date + timedelta(days=30, hours=23)

    reports = asyncio.run(
        get_reports(icao.upper(), report_type, str(init_date), str(final_date))
    )
    if remove_white_spaces:
        reports = remove_spaces(reports)

    with open(f"./{filename}", "w") as f:
        for report in reports:
            f.write(report + "\n")


if __name__ == "__main__":
    app()