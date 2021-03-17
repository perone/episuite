import datetime
import io
import json
import re
import typing
from typing import Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

from episuite import data


class FacebookSymptomSurvey:
    """This is a class implementing a client for the COVID-19 World Survey Data API
    from Facebook and the University of Maryland.

    .. seealso:: Please see :cite:t:`Maryland2021` for more information
                 about the COVID-19 World Survey Data API.
    """
    def __init__(self, base_url: str = "https://covidmap.umd.edu/api") -> None:
        self.base_url = base_url

    def get_survey_country_region(self) -> Dict:
        """Get the survey country/region list."""
        r = requests.get(f"{self.base_url}/region")
        return r.json()["data"]

    def get_survey_date_avail(self, country_name: str, region_name: str) -> Dict:
        """Retrieve all dates for survey responses for a place.

        :param country_name: the name of the country
        :param region_name: name of the region.
        """
        payload: Dict[str, str] = {
            "country": country_name,
            "region": region_name,
        }
        base_url = f"{self.base_url}/datesavail"
        r = requests.get(base_url, params=payload)
        return r.json()["data"]

    def get_survey_range(self, country_name: str,
                         region_name: str,
                         start_date: str, end_date: str,
                         type_: str = "daily",
                         indicator: str = "covid") -> Dict:
        """Retrieve data for a particular indicator.

        :param country_name: the name of the country
        :param region_name: name of the region.
        :param start_date: start date in the format (YYYYMMDD),
                           example: 20200921.
        :param end_date: start date in the format (YYYYMMDD),
                         example: 20200921.
        :param type_: can be "daily" or "smoothed"
        :param indicator: can be "covid", "mask" or "vaccine_acpt"
        """
        payload: Dict[str, str] = {
            "indicator": indicator,
            "type": type_,
            "country": country_name,
            "region": region_name,
            "daterange": f"{start_date}-{end_date}",
        }
        base_url = f"{self.base_url}/resources"
        r = requests.get(base_url, params=payload)
        return r.json()["data"]


class MovementRangeDateURL(typing.NamedTuple):
    date: datetime.date
    url: str


class FacebookMovementRange:
    """This is a client API for Facebook Movement Range data.

    .. seealso:: Please look at `HDX Movement Range Maps
                 <https://data.humdata.org/dataset/movement-range-maps>`_
                 for more information about this data.
    """
    MAIN_RESOURCE_URL = "https://data.humdata.org/dataset/movement-range-maps"

    def _get_last_date_available(self) -> MovementRangeDateURL:
        with io.BytesIO() as bio:
            data.download_remote(self.MAIN_RESOURCE_URL,
                                 bio, show_progress=False)
            value = bio.getvalue()
        soup = BeautifulSoup(value.decode("utf-8"), "html.parser")
        parsed_json: Dict = json.loads("".join(soup.find("script", {
            "type": "application/ld+json"
        }).contents))

        for item in parsed_json["@graph"]:
            if "schema:name" not in item:
                continue
            schema_name: str = item["schema:name"]
            if schema_name.startswith("movement-range-data-"):
                y, m, d = re.findall(r'(\d{4})-(\d{2})-(\d{2})',
                                     schema_name)[0]
                last_available = pd.to_datetime(f"{y}/{m}/{d}",
                                                format="%Y/%m/%d")
                url = item["schema:contentUrl"]
                break
        return MovementRangeDateURL(last_available.date(), url)
