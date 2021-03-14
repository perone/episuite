from typing import List

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import dates as mdates
from matplotlib import pyplot as plt


class Durations:
    COLUMN_START: str = "DATE_START"
    COLUMN_END: str = "DATE_END"
    COLUMN_STAY_DURATION: str = "__EPISUITE_STAY_DURATION"

    COLUMNS: List[str] = [COLUMN_START, COLUMN_END]

    def __init__(self, df_durations: pd.DataFrame, filter_gt: bool = True):
        self.df_durations = df_durations.copy()
        self.filter_gt = filter_gt
        self.check_dataframe()

        # Filter only valid durations, where end is
        # greater than or equal to the start
        if self.filter_gt:
            gt_query = self.df_durations[self.COLUMN_END] >= \
                self.df_durations[self.COLUMN_START]
            self.df_durations = self.df_durations[gt_query]

        diff = self.df_durations[self.COLUMN_END] \
            - self.df_durations[self.COLUMN_START]
        self.df_durations[self.COLUMN_STAY_DURATION] = diff.dt.days
        self.plot = DurationsPlot(self)

    def get_dataframe(self) -> pd.DataFrame:
        return self.df_durations

    def check_dataframe(self) -> None:
        if not set(self.COLUMNS).issubset(self.df_durations.columns):
            raise ValueError(f"The dataframe should have {Durations.COLUMNS=}")

    def get_stay_distribution(self) -> np.ndarray:
        diff = self.df_durations[self.COLUMN_END] - self.df_durations[self.COLUMN_START]
        return diff.dt.days.values


class DurationsPlot:
    """Makes plots for the durations

    :param duration: the duration
    """

    def __init__(self, duration: Durations):
        self.duration = duration

    def histogram(self, **kwargs):
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

    def density(self, **kwargs):
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

    def timeplot(self, locator: str = "month", interval: int = 1, **kwargs):
        df = self.duration.get_dataframe()
        ax = sns.lineplot(
            data=df,
            x=Durations.COLUMN_START,
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
