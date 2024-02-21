import asyncio
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import List

import typer

from .get import get_reports
from .sanitize import sanitize_all, sanitize_metar, sanitize_taf

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
        "metar.txt",
        "--file",
        "-F",
        help="The filename to write the reports on disk. Default will be changed",
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
    sanitize: bool = typer.Option(
        False,
        "--sanitize",
        "-s",
        is_flag=True,
        help="Sanitize the report to use in TAF verification program.",
    ),
    datetime_prefix: bool = typer.Option(
        True,
        is_flag=True,
        help="Add the date and time as a prefix of the reports with format `%Y%m%d%H%M`",
    ),
) -> None:
    if init_date > datetime.today():
        typer.echo(f"Initial date and time must be older than current date and time.")
        return

    if report_type == "FT" or report_type == "FC":
        filename = "taf.txt"
    elif report_type == "ALL":
        filename = "observations.txt"
        taf_filename = "taf.txt"
    elif report_type == "SP":
        filename = "speci.txt"
    else:
        pass

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

    if report_type in ["SA", "SP", "FC", "FT"]:
        with open(f"./{filename}", "w") as f:
            for report in reports:
                if sanitize:
                    if report_type in ["SA", "SP"]:
                        report = sanitize_metar(report, icao)
                    elif report_type in ["FC", "FT"]:
                        report = sanitize_taf(report, icao)
                if datetime_prefix:
                    f.write(report + "\n")
                else:
                    f.write(re.sub(r"\d{12}\s", "", report) + "\n")
    else:
        obs_file = open(f"./{filename}", "w")
        taf_file = open(f"./{taf_filename}", "w")
        for report in reports:
            is_obs = "METAR" in report or "SPECI" in report

            if sanitize:
                report = sanitize_all(report, icao, is_obs)

            text_to_write = ""
            if datetime_prefix:
                text_to_write = report + "\n"
            else:
                text_to_write = re.sub(r"\d{12}\s", "", report) + "\n"

            if is_obs:
                obs_file.write(text_to_write)
            else:
                taf_file.write(text_to_write)

        obs_file.close()
        taf_file.close()

    if report_type == "ALL":
        report_filename = "OBSERVATIONS and TAF"
    else:
        report_filename = filename.replace(".txt", "").upper()
    if len(reports) > 0:
        typer.echo(f"{len(reports)} {report_filename} requested succesfully.")
    if len(reports) == 0:
        typer.echo(f"No {report_filename} requested.")


if __name__ == "__main__":
    app()
