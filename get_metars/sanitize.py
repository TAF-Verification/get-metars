import re
from datetime import datetime, timedelta

# from metar import Metar
import typer


def _sanitize_type_metar(metar: str, icao_code: str):
    metar = re.sub(r"(METAR\s+)?SPECI(\s+METAR)?", "METAR", metar)
    metar = metar.replace("COR", "")
    metar = metar.replace("ZZ", "Z")

    if metar.count("METAR") == 0:
        icao = icao_code.upper()
        metar = metar.replace(icao, f"METAR {icao}")

    return metar


def _sanitize_wind(report: str):
    report = report.replace("KTKT", "KT")

    format = r"\s(?P<dir>\d{3})(?P<speed>\d{2})(?P<g>G?)(?P<gust>\d{2}?)(?P<units>(KT|MPS|KTS)?)\s"
    pattern = re.compile(format)

    matches = re.search(pattern, report)

    if matches:
        if matches.group("g") is None and matches.group("gust") is not None:
            correct_format = f'{matches.group("dir")}{matches.group("speed")}G{matches.group("gust")}{matches.group("units")}'
            report = re.sub(format, correct_format, report)

    report = re.sub(r"\d{3}V\d{3}", "", report)

    return report


def _sanitize_weather(report: str):
    report = re.sub(r"DZ|SHRA", "RA", report)
    report = re.sub(r"BR|HZ|[BP][CR]FG", "FG", report)
    report = re.sub(r"(FG\s){2,}", "FG ", report)
    report = re.sub(r"VC[A-Z][A-Z]", "", report)
    report = re.sub(r"\+|-", "", report)

    return report


def _sanitize_visibility(report: str):
    report = report.replace("CAVOK", "9999")
    report = re.sub(r"9999\s{2,}|99999", "9999 ", report)
    report = re.sub(r"\s\d{3,4}[NS]([ENSW])?([EW])?", "", report)
    report = re.sub(
        r"R\d{2}([A-Z])?/(P|M)?\d{4}(V(P|M)?\d{4})?(FT)?([NDU])?", "", report
    )

    return report


def _sanitize_cloud(report: str):
    report = re.sub(r"VV///|NSC", "", report)
    report = re.sub(r"\s(GEW|FWE|HEW|FE[A-Z]W|F[A-Z]EW)", " FEW", report)
    report = re.sub(r"\s(ACT|STC|DCT|SC[A-Z]T|S[A-Z]CT)", " SCT", report)
    report = re.sub(r"\s(VKN|BNK|NNK|BK[A-Z]N|B[A-Z]KN)", " BKN", report)
    report = re.sub(r"\s(IVC|PVC|OV[A-Z]C|O[A-Z]VC)", " OVC", report)
    report = re.sub(r"TCU|TUC|CB", "", report)

    return report


def _remove_suplementary_info(metar: str):
    metar = re.sub(
        r"\sWS\s?(R?(/|\s+)?\d{2,}|(ALL)?\s?R[WNU]+Y\s?\d{2,}).*", "=", metar
    )
    metar = re.sub(r"\sRE[A-Z]{2,}.*", "=", metar)

    return metar


def _remove_rmk_and_trend_indicator(metar: str):
    metar = re.sub(r"\s?RMK.+", "=", metar)
    metar = re.sub(
        r"\s?(BECMG|BECMG(0|O|\??\s?\?+)|VECMG|BCMG|BECMG/|BECM/|BCMG/|BECOMG|BECGM|BECM\sG)(.+)?",
        "=",
        metar,
    )
    metar = re.sub(
        r"\s?(NOSIG|NOPSIG|NSIG|NPSIG|NOZIG|NOPZIG|NOSOG|MOSIG|NISIG|NOSGI|NOSI\sG|NOSIG0|NSOIG|NOSIIG)(.+)?",
        "=",
        metar,
    )
    metar = re.sub(r"\s?(TEMPO|TMPO|TEMPOO|TMEPO|TEMOP|TEMO|TEMP\sO)(.+)?", "=", metar)

    return metar


# TODO: Enable parsing of reports when possible
# def parse_metar(metar: str):
#     code = metar.replace("=", "")
#     code = re.sub(r"^\d{12}\s", "", code)
#     code = code.strip()

#     date = datetime.strptime(metar[:12], "%Y%m%d%H%M")

#     try:
#         if not "NIL" in metar:
#             metar_obj = Metar.Metar(code, month=date.month, year=date.year)
#     except Metar.ParserError as e:
#         typer.echo(f"{e}")


def sanitize_metar(metar: str, icao_code: str):
    metar = _remove_rmk_and_trend_indicator(metar)
    metar = _remove_suplementary_info(metar)
    metar = _sanitize_type_metar(metar, icao_code)
    metar = _sanitize_wind(metar)
    metar = _sanitize_visibility(metar)
    metar = _sanitize_weather(metar)
    metar = _sanitize_cloud(metar)

    metar = re.sub(r"={2,}", "=", metar)
    metar = re.sub(r"\s{2,}", " ", metar)

    #    parse_metar(metar)

    return metar


def _sanitize_type_taf(taf: str, icao_code: str):
    taf = re.sub(r"COR|AMD", "", taf)

    if taf.count("TAF") == 0:
        icao = icao_code.upper()
        taf = taf.replace(icao, f"TAF {icao}")

    return taf


def _sanitize_validity_period(taf: str):
    format = r"^\d{12}\s"
    pattern = re.compile(format)
    match = re.match(pattern, taf)

    if match:
        date = datetime.strptime(taf[:12], "%Y%m%d%H%M")
        format = r"\s\d{2}00/\d{2}00\s"
        pattern = re.compile(format)
        period_match = re.search(pattern, taf)

        if period_match:
            period_date = date + timedelta(days=1)
            period_day = (
                f"{period_date.day}" if period_date.day >= 10 else f"0{period_date.day}"
            )
            taf = re.sub(format, f" {period_day}00/{period_day}24 ", taf)

    return taf


def _sanitize_change_group_code(taf: str):
    taf = re.sub(
        r"BECMG0|VECMG|BCMG|BECMG/|BECM/|BCMG/|BECOMG|BECGM|BECM\sG", "BECMG", taf
    )
    taf = re.sub(
        r"NOPSIG|NSIG|NPSIG|NOZIG|NOPZIG|NOSOG|MOSIG|NISIG|NOSGI|NOSI\sG|NOSIG0|NSOIG|NOSIIG",
        "NOSIG",
        taf,
    )
    taf = re.sub(r"TMPO|TEMPOO|TMEPO|TEMOP|TEMO|TEMP\sO", "TEMPO", taf)

    return taf


def sanitize_taf(taf: str, icao_code: str):
    taf = _sanitize_type_taf(taf, icao_code)
    taf = _sanitize_validity_period(taf)
    taf = _sanitize_wind(taf)
    taf = _sanitize_visibility(taf)
    taf = _sanitize_weather(taf)
    taf = _sanitize_cloud(taf)
    taf = _sanitize_change_group_code(taf)

    return taf
