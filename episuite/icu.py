import concurrent.futures

import arviz as az
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from tqdm.auto import tqdm

from episuite.distributions import DurationDistribution


class ICUAdmissions:
    """This class will wrap admissions (Series) and will
    provide utility methods to handle ICU admissions.

    :param s_admissions: a series with dates in the index
                         and admissions for each day.
    """
    def __init__(self, s_admissions: pd.Series):
        self.s_admissions = s_admissions.copy()
        self.s_admissions.sort_index(inplace=True, ascending=True)
        if len(self.s_admissions) <= 0:
            raise ValueError("Empty admission series.")
        self.s_admissions.index = s_admissions.index.date
        self.plot = ICUAdmissionsPlot(self)

    def sanity_check(self) -> None:
        index_duplicates = self.s_admissions.index.duplicated().sum()
        if index_duplicates > 0:
            raise ValueError(f"{index_duplicates} duplicated dates in the index.")

        diff_dates = np.diff(self.s_admissions.index)
        for i, date in enumerate(diff_dates):
            if date.days != 1:
                date_diff_before = self.s_admissions.index[i + 1]
                date_diff_after = self.s_admissions.index[i + 1]
                raise ValueError(f"Date {date_diff_after} with a gap of {date.days} days "
                                 f"from the previous date {date_diff_before}.")

    def get_admissions_series(self) -> pd.Series:
        return self.s_admissions

    def __repr__(self) -> str:
        sum_admissions = self.s_admissions.sum()
        entries = len(self.s_admissions)
        return f"ICUAdmissions[Entries={entries}, " \
            f"Total Admissions={sum_admissions}]>"


class ICUAdmissionsPlot:
    def __init__(self, icu_admissions: ICUAdmissions):
        self.icu_admissions = icu_admissions

    def bar(self, locator: str = "month", interval: int = 1) -> None:
        s_adm = self.icu_admissions.get_admissions_series()
        plt.bar(s_adm.index, s_adm.values)
        ax = plt.gca()
        loc = mdates.MonthLocator(interval=interval)
        formatter = mdates.DateFormatter(fmt="%b %Y")
        if locator == "day":
            loc = mdates.DayLocator(interval=interval)
            formatter = mdates.DateFormatter(fmt="%d %b %Y")
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        ax.figure.autofmt_xdate(rotation=90, ha='center')
        ax.set_xlabel("Admission date")
        ax.set_ylabel("Number of admissions")
        plt.title("ICU Admissions per date")
        sns.despine()
        return ax


class ICUSimulation:
    def __init__(self, admissions: ICUAdmissions,
                 duration_distribution: DurationDistribution):
        self.admissions = admissions
        self.duration_distribution = duration_distribution

    def get_admissions(self) -> ICUAdmissions:
        return self.admissions

    def get_duration_distribution(self) -> DurationDistribution:
        return self.duration_distribution

    def simulation_round(self):
        s_admissions = self.admissions.get_admissions_series()
        admission_counts = s_admissions.values.astype(np.int32)
        dates = s_admissions.index
        dates_rep = np.repeat(dates, admission_counts)

        num_samples = len(dates_rep)
        los = self.duration_distribution.sample(num_samples)

        ran = [pd.date_range(los_date, periods=los_sample)
               for los_sample, los_date in zip(los, dates_rep)]

        new_dates_rep = pd.DatetimeIndex([]).append(ran)
        vals = pd.Series(new_dates_rep).value_counts().sort_index()
        return vals

    def simulate(self, iterations=10, show_progress: bool = True):
        simulations = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.simulation_round)
                       for _ in range(iterations)]

            for future in tqdm(concurrent.futures.as_completed(futures),
                               total=len(futures), desc="Simulation",
                               disable=not show_progress):
                simulations.append(future.result())

        df_simulation = pd.concat(simulations, axis=1)
        df_simulation = df_simulation.fillna(0)
        return ICUSimulationResults(self, df_simulation)


class ICUSimulationResults:
    def __init__(self, icu_simulation: ICUSimulation,
                 df_simulation: pd.DataFrame):
        self.df_simulation = df_simulation
        self.icu_simulation = icu_simulation
        self.plot = ICUSimulationResultsPlot(self)

    def get_admissions(self) -> ICUAdmissions:
        return self.icu_simulation.get_admissions()

    def get_simulation_results(self) -> pd.DataFrame:
        return self.df_simulation

    def hdi(self):
        dates_idx = []
        lb95_idx = []
        ub95_idx = []
        lb50_idx = []
        ub50_idx = []
        mean_idx = []
        median_idx = []

        for item in self.df_simulation.iterrows():
            lb95, ub95 = az.hdi(item[1].values, hdi_prob=0.95)
            lb50, ub50 = az.hdi(item[1].values, hdi_prob=0.50)
            mean = np.mean(item[1].values)
            median = np.median(item[1].values)
            dates_idx.append(item[0])
            lb95_idx.append(lb95)
            ub95_idx.append(ub95)
            lb50_idx.append(lb50)
            ub50_idx.append(ub50)
            mean_idx.append(mean)
            median_idx.append(median)

        df_final = pd.DataFrame({
            "date": dates_idx,
            "lb95": lb95_idx,
            "ub95": ub95_idx,
            "lb50": lb50_idx,
            "ub50": ub50_idx,
            "mean_val": mean_idx,
            "median_val": median_idx,
        })
        return df_final


class ICUSimulationResultsPlot:
    def __init__(self, simulation_results: ICUSimulationResults):
        self.simulation_results = simulation_results

    def lineplot(self):
        df_hdi = self.simulation_results.hdi()
        plt.plot(df_hdi.date, df_hdi.mean_val, color="orange", label="Estimated ICU Occupation")
        plt.fill_between(df_hdi.date, df_hdi.lb95, df_hdi.ub95, color="C1", alpha=0.3, label="95% credibility interval")
        plt.fill_between(df_hdi.date, df_hdi.lb50, df_hdi.ub50, color="C1", alpha=0.3)
        plt.grid(lw=0.5, linestyle=":", which="both")

        adm = self.simulation_results.get_admissions()
        s_admissions: pd.Series = adm.get_admissions_series()
        plt.axvline(s_admissions.index.max(), color="black", linestyle="--", lw=0.8)
        sns.despine()
        plt.bar(s_admissions.index, s_admissions.values, label="Admissions per day")
        plt.xlabel("Date")
        plt.ylabel("ICU Occupancy (number of patients)")
        plt.legend()
