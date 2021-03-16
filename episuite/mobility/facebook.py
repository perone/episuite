from typing import Dict

import requests


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
