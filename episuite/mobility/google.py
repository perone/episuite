from typing import Any, Optional

import pandas as pd
import seaborn as sns
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from episuite import data


class GoogleMobility:
    """This is a class implementing a client for the Google
    Community Mobility Reports.

    .. seealso::
        `Google Community Mobility Report <https://www.google.com/covid19/mobility/>`_
            Community Mobility Report website.

    :param report_url: alternative report download link
    """
    DEFAULT_REPORT_URL: str = \
        "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"

    def __init__(self, report_url: Optional[str] = None):
        self.report_url = report_url or GoogleMobility.DEFAULT_REPORT_URL

    def load_report(self, country_region_code: Optional[str] = None,
                    show_progress: bool = True, cache: bool = True) -> pd.DataFrame:
        """Load the report from Google and optionally cache it or fitler
        by a country code. Given that the mobility report is a large file,
        it is highly recommended to specify the country region code.

        :param country_region_code: The country region code, i.e. "BR"
                                    for Brazil.
        :param show_progress: Show a progress bar for the download
        :param cache: If cache should be done or not, default to True
        :returns: a dataframe with the results already filtered and parsed
        """
        fpath = data.load_from_cache(self.report_url, "google_mobility.csv",
                                     "Google Mobility Report",
                                     show_progress=show_progress,
                                     invalidate=not cache)
        if country_region_code is None:
            df = pd.read_csv(fpath, low_memory=False,
                             parse_dates=["date"])
        else:
            iter_csv = pd.read_csv(fpath, low_memory=False,
                                   parse_dates=["date"],
                                   iterator=True, chunksize=5000)
            df = pd.concat([chunk[chunk['country_region_code'] == country_region_code]
                            for chunk in iter_csv])
        return df
