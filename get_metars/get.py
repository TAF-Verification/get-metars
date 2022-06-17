import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup, ResultSet
from pydantic import validator
from pydantic.dataclasses import dataclass
from typing_extensions import Literal

today = datetime.today()


@dataclass
class DateInitPayload:
    date: Optional[datetime]

    @validator("date")
    def parse_date(cls, v: str):
        if isinstance(v, str):
            try:
                date = datetime.strptime(v, "%Y-%m-%dT%H:%M")
            except ValueError:
                return datetime.today()
            else:
                return date

        return v

    @property
    def to_dict(self) -> Dict[str, str]:
        return {
            "ano": f"{self.date.year}",
            "mes": f"{self.date.month:02d}",
            "day": f"{self.date.day:02d}",
            "hora": f"{self.date.hour:02d}",
        }


class DateFinalPayload(DateInitPayload):
    @property
    def to_dict(self) -> Dict[str, str]:
        return {
            "anof": f"{self.date.year}",
            "mesf": f"{self.date.month:02d}",
            "dayf": f"{self.date.day:02d}",
            "horaf": f"{self.date.hour:02d}",
            "minf": f"{self.date.minute:02d}",
        }


@dataclass
class Payload:
    icao: str
    type_: Literal["ALL", "SA", "SP", "FT", "FC"]
    ord_: Literal["REV", "DIR"]
    nil: Literal["SI", "NO"]
    fmt: Literal["html", "txt"]

    @validator("icao")
    def must_be_a_valid_icao_code(cls, v: str) -> str:
        assert len(v) == 4, "ICAO code must be 4 characters lenght"
        assert v.isalnum(), "invalid characters in ICAO code"
        return v

    @property
    def to_dict(self) -> Dict[str, str]:
        return {
            "lugar": self.icao,
            "tipo": self.type_,
            "ord": self.ord_,
            "nil": self.nil,
            "fmt": self.fmt,
            "enviar": "Ver",
        }


def validate_dates(init: datetime, final: datetime):
    delta = final - init
    assert final > init, "final date must be most recent than init date"
    assert delta.days <= 31, "only requests of 31 days are valid"


OGIMET_METAR_URL = "http://ogimet.com/display_metars2.php"


def process_tr_tags(tr_tags: ResultSet) -> List[str]:
    reports: List[str] = []
    for tag in tr_tags:
        td_tags = tag.findAll("td")
        report = td_tags[2].find("pre").string
        date = td_tags[1].string.replace("->", "")
        _datetime = datetime.strptime(date, "%d/%m/%Y %H:%M")
        reports.append(f"{_datetime.strftime('%Y%m%d%H%M')} {report}")
    return reports


async def get_data(payload: Dict[str, str]) -> List[str]:
    async with aiohttp.request("GET", OGIMET_METAR_URL, params=payload) as resp:
        data = await resp.text()
        soup = BeautifulSoup(data, "html5lib")
        tr_tags = soup.find_all(name="tr", attrs={"bgcolor": re.compile(r".+")})

        return process_tr_tags(tr_tags)


async def get_reports(icao: str, type_: str, init: str, final: str) -> None:
    # Init dates
    init_date = DateInitPayload(date=init)
    final_date = DateFinalPayload(date=final)
    # Validate dates
    validate_dates(init_date.date, final_date.date)
    # Init payload
    payload_instance = Payload(icao=icao, type_=type_, ord_="DIR", nil="SI", fmt="html")
    payload = payload_instance.to_dict
    # Update payload with valid dates
    payload.update(init_date.to_dict)
    payload.update(final_date.to_dict)
    # Getting the data
    reports = await get_data(payload)
    # Return the reports as a List[str]
    return reports


if __name__ == "__main__":
    reports = asyncio.run(get_reports("FT", "2015-01-01T00:00", "2015-01-31T23:00"))
    for report in reports:
        print(report)
