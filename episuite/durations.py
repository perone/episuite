from typing import Any, Dict

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from episuite import distributions


class Durations:
    COLUMN_STAY_DURATION: str = "__EPISUITE_STAY_DURATION"

    def __init__(self, df_durations: pd.DataFrame,
                 column_start: str = "DATE_START",
                 column_end: str = "DATE_END",
                 filter_gt: bool = True):
        self.df_durations = df_durations.copy()
        self.filter_gt = filter_gt
        self.column_start = column_start
        self.column_end = column_end
        self._check_dataframe()

        # Filter only valid durations, where end is
        # greater than or equal to the start
        if self.filter_gt:
            gt_query = self.df_durations[self.column_end] >= \
                self.df_durations[self.column_start]
            self.df_durations = self.df_durations[gt_query]

        diff = self.df_durations[self.column_end] \
            - self.df_durations[self.column_start]
        self.df_durations[self.COLUMN_STAY_DURATION] = diff.dt.days
        self.plot = DurationsPlot(self)

    def _check_dataframe(self) -> None:
        columns = set([self.column_start, self.column_end])
        if not set(columns).issubset(self.df_durations.columns):
            raise ValueError(f"The dataframe should have columns: {columns}.")

    def get_dataframe(self) -> pd.DataFrame:
        return self.df_durations

    def get_stay_distribution(self) -> np.ndarray:
        diff = self.df_durations[self.column_end] - self.df_durations[self.column_start]
        return diff.dt.days.values

    def get_bootstrap(self) -> distributions.EmpiricalBootstrap:
        stay_distribution: np.ndarray = self.get_stay_distribution()
        return distributions.EmpiricalBootstrap(stay_distribution)


class DurationsPlot:
    """Makes plots for the durations

    :param duration: the duration
    """

    def __init__(self, duration: Durations):
        self.duration = duration

    def histogram(self, **kwargs: Dict) -> Any:
        df = self.duration.get_dataframe()
        ax = sns.histplot(
            df,
            x=Durations.COLUMN_STAY_DURATION,
            edgecolor=".3",
            linewidth=.5,
            **kwargs
        )
        ax.set_xlabel("Duration (in days)")
        ax.set_ylabel("Count")
        sns.despine()
        return ax

    def density(self, **kwargs: Dict) -> Any:
        df = self.duration.get_dataframe()
        ax = sns.displot(
            df,
            x=Durations.COLUMN_STAY_DURATION,
            kind="kde",
            cut=0,
            **kwargs
        )
        plt.xlabel("Duration (in days)")
        sns.despine()
        return ax

    def timeplot(self, locator: str = "month",
                 interval: int = 1, **kwargs: Dict) -> Any:
        df = self.duration.get_dataframe()
        ax = sns.lineplot(
            data=df,
            x=self.duration.column_start,
            y=Durations.COLUMN_STAY_DURATION,
            lw=0.8,
            **kwargs
        )
        plt.axhline(df.mean(numeric_only=True)[Durations.COLUMN_STAY_DURATION],
                    color="black", linestyle="--", lw=0.8, label="Mean")
        loc = mdates.MonthLocator(interval=interval)
        formatter = mdates.DateFormatter(fmt="%b %Y")
        if locator == "day":
            loc = mdates.DayLocator(interval=interval)
            formatter = mdates.DateFormatter(fmt="%d %b %Y")
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        ax.figure.autofmt_xdate(rotation=90, ha='center')
        sns.despine()
        plt.ylabel("Stay (in days)")
        plt.xlabel("Start date")
        plt.legend()
        return ax
