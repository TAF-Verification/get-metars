import asyncio
from datetime import datetime, timedelta
from typing import List
import re
from enum import Enum

import typer

from .get import get_reports

app = typer.Typer()


def remove_white_spaces(reports: List[str]):
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
        ReportType.SA,
        "--type",
        "-t",
        help="""Type of report to request.
        SA -> METAR,
        SP -> SPECI,
        FT -> TAF (long),
        FC -> TAF (short),
        ALL -> All types""",
    ),
    init_date: datetime = typer.Option(
        "2006-01-01T00:00:00",
        "--init",
        "-i",
        help="The initial UTC date and time to request the reports.",
    ),
    final_date: datetime = typer.Option(
        None,
        "--final",
        "-f",
        help=(
            "The final UTC date and time to request the reports. "
            "Defaults to `init` + 30 days, 23 hours and 59 minutes."
        ),
    ),
    filename: str = typer.Option(
        "reports.txt",
        "--file",
        "-F",
        help="The filename to write the reports on disk.",
    ),
    one_line: bool = typer.Option(
        False,
        "--one-line",
        "-o",
        is_flag=True,
        help=(
            "Remove white spaces in the reports. "
            "If True reports will be written in one line."
        ),
    ),
) -> None:
    if report_type == "FT" or report_type == "FC":
        report_filename = "taf"
    elif report_type == "SA":
        report_filename = "metar"
    elif report_type == "SP":
        report_filename = "speci"
    else:
        pass

    filename = f"{report_filename}.txt"

    if final_date is None:
        final_date = init_date + timedelta(days=30, hours=23, minutes=59)
    typer.echo(f"Request from {init_date} to {final_date}.")

    reports: List[str] = []
    try:
        reports = asyncio.run(
            get_reports(icao.upper(), report_type, str(init_date), str(final_date))
        )
    except Exception as e:
        typer.echo(f"{e}.".capitalize())
    else:
        if one_line:
            reports = remove_white_spaces(reports)

    with open(f"./{filename}", "w") as f:
        for report in reports:
            f.write(report + "\n")

    if len(reports) > 0:
        typer.echo(f"{len(reports)} {report_filename.upper()} requested succesfully.")
    if len(reports) == 0:
        typer.echo(f"No {report_filename.upper()} requested.")


if __name__ == "__main__":
    app()
