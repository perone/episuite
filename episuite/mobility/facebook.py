import datetime
import io
import json
import re
import typing
from pathlib import Path
from typing import Any, Dict, Optional
from zipfile import ZipFile

import pandas as pd
import requests
import seaborn as sns
from bs4 import BeautifulSoup
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from episuite import data


class FacebookSymptomSurvey:
    """This is a class implementing a client for the COVID-19 World Survey Data API
    from Facebook and the University of Maryland.

    .. seealso:: Please see :cite:t:`Maryland2021` for more information
                 about the COVID-19 World Survey Data API.
    """
    def __init__(self, base_url: str = "https://covidmap.umd.edu/api") -> None:
        self.base_url = base_url

    def get_survey_country_region(self) -> pd.DataFrame:
        """Get the survey country/region list."""
        r = requests.get(f"{self.base_url}/region")
        return pd.DataFrame(r.json()["data"])

    def get_survey_date_avail(self, country_name: str, region_name: str) -> pd.DataFrame:
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
        return pd.DataFrame(r.json()["data"])

    def get_survey_range(self, country_name: str,
                         region_name: str,
                         start_date: str, end_date: str,
                         type_: str = "daily",
                         indicator: str = "covid") -> pd.DataFrame:
        """Retrieve data for a particular indicator. This method
        will return a DataFrame with pre-computed confidence
        intervals (percent_cli_95_upper_ci/percent_cli_95_lower_ci).

        .. seealso:: Please see :cite:t:`Maryland2021` for more information
                    about the COVID-19 World Survey Data API.

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
        r = r.json()["data"]

        df = pd.DataFrame(r)
        df["survey_date"] = pd.to_datetime(df.survey_date, format="%Y%m%d")
        df["percent_cli_95_upper_ci"] = (df.percent_cli + (1.96 * df.cli_se)) * 100.0
        df["percent_cli_95_lower_ci"] = (df.percent_cli - (1.96 * df.cli_se)) * 100.0
        return df

    @staticmethod
    def plot_region_percent_cli(df_survey_range: pd.DataFrame,
                                locator: str = "month",
                                interval: int = 1) -> Any:
        """Plot the CLI (Covid-like illness) from the results
        of a region.

        :param df_survey_range: the results from the survey
        :param locator: can be "month" or "day", to define the
                        location of ticks in the plot for the dates
        :param interval: interval to show the date labels in the plot
        """
        plt.plot(df_survey_range["survey_date"],
                 df_survey_range.percent_cli * 100.0, color="red", lw=0.8,
                 marker='o', markersize=5, markerfacecolor='w')
        ax = plt.gca()
        ax.fill_between(df_survey_range["survey_date"],
                        df_survey_range.percent_cli_95_upper_ci,
                        df_survey_range.percent_cli_95_lower_ci,
                        alpha=0.2, lw=1.5, color="C1")

        loc = mdates.MonthLocator(interval=interval)
        formatter = mdates.DateFormatter(fmt="%b %Y")

        if locator == "day":
            loc = mdates.DayLocator(interval=interval)
            formatter = mdates.DateFormatter(fmt="%d %b %Y")

        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        ax.figure.autofmt_xdate(rotation=90, ha='center')

        plt.grid(axis="both", which="major", linestyle="--", alpha=0.4)

        plt.xlabel("Dates")
        plt.ylabel("Weighted percentage w/ COVID-like illness")

        plt.title("Facebook symptoms survey")
        sns.despine()
        plt.tight_layout()
        return ax


class MovementRangeResource(typing.NamedTuple):
    date: datetime.date
    url: str
    filename: str


class FacebookMovementRange:
    """This is a client API for Facebook Movement Range data.

    .. seealso:: Please look at `HDX Movement Range Maps
                 <https://data.humdata.org/dataset/movement-range-maps>`_
                 for more information about this data.
    """
    MAIN_RESOURCE_URL = "https://data.humdata.org/dataset/movement-range-maps"

    def _get_last_date_available(self) -> MovementRangeResource:
        with io.BytesIO() as bio:
            data.download_remote(self.MAIN_RESOURCE_URL,
                                 bio, "Movement Range Maps",
                                 show_progress=False)
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

        return MovementRangeResource(last_available.date(), url, schema_name)

    def _download_cache_resource(self, resource: MovementRangeResource,
                                 show_progress: bool = True) -> Path:
        cached_file = data.load_from_cache(resource.url, resource.filename,
                                           "Downloading movement range data",
                                           show_progress=show_progress)
        return cached_file

    def load_movement_range(self, country_code: Optional[str] = None,
                            show_progress: bool = True) -> pd.DataFrame:
        """This method will load the movement range data and optionally
        filter for the specified country code.

        :param country_code: country code (i.e. 'BRA' for Brazil)
        :param show_progress: show download progress
        :returns: a DataFrame with the movement range dataset
        """
        last_resource = self._get_last_date_available()
        cached_file = self._download_cache_resource(last_resource, show_progress)
        zip_file = ZipFile(cached_file)

        fname = "<not found>"
        for fobj in zip_file.filelist:
            if fobj.filename.startswith("movement-range"):
                fname = fobj.filename

        with zip_file.open(fname, "r") as mrange:
            if country_code is None:
                df = pd.read_csv(mrange, delimiter="\t", low_memory=False)
            else:
                iter_csv = pd.read_csv(mrange, delimiter="\t",
                                       iterator=True, chunksize=5000)
                df = pd.concat([chunk[chunk['country'] == country_code]
                               for chunk in iter_csv])
        return df
