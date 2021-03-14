import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt

from episuite import data, distributions, durations, icu


class TestICUAdmissions:
    @pytest.fixture
    def mock_admissions(self) -> pd.Series:
        index = pd.date_range("2020-01-01 00:00:01", "2020-01-10 00:10:00")
        data = np.arange(len(index))
        return pd.Series(data, index=index)

    @pytest.fixture
    def mock_admissions_repeated(self) -> pd.Series:
        index = pd.date_range("2020-01-01", "2020-01-05")
        index_continue = pd.date_range("2020-01-01", "2020-01-05")
        index = index.append(index_continue)
        data = np.arange(len(index))
        return pd.Series(data, index=index).sort_index()

    @pytest.fixture
    def mock_irregular_admissions(self) -> pd.Series:
        index = pd.date_range("2020-01-01", "2020-01-05")
        index_continue = pd.date_range("2020-01-08", "2020-01-10")
        index = index.append(index_continue)
        data = np.arange(len(index))
        return pd.Series(data, index=index)

    def test_empty(self) -> None:
        series = pd.Series(dtype=np.float32)
        with pytest.raises(ValueError, match="Empty"):
            _ = icu.ICUAdmissions(series)

    def test_repeated_date(self, mock_admissions_repeated: pd.Series) -> None:
        adm = icu.ICUAdmissions(mock_admissions_repeated)
        with pytest.raises(ValueError, match="duplicated"):
            adm.sanity_check()

    def test_regular(self, mock_admissions: pd.Series) -> None:
        adm = icu.ICUAdmissions(mock_admissions)
        adm.sanity_check()

    def test_date_gap(self, mock_irregular_admissions: pd.Series) -> None:
        adm = icu.ICUAdmissions(mock_irregular_admissions)
        with pytest.raises(ValueError, match="with a gap"):
            adm.sanity_check()

    def test_repr(self, mock_admissions: pd.Series) -> None:
        adm = icu.ICUAdmissions(mock_admissions)
        rep = repr(adm)
        assert "Entries" in rep

    def test_plot(self, mock_admissions: pd.Series) -> None:
        adm = icu.ICUAdmissions(mock_admissions)
        
        adm.plot.bar()
        plt.close()


class TestICUSimulation:
    def test_simulate(self) -> None:
        sample_data = data.admissions_sample()
        # Filter some dates to avoid hitting a timeout on testing in CI
        sample_data = sample_data[sample_data["DATE_START"] >= "2021-01-01"]

        sample_data_admissions = sample_data.groupby("DATE_START").size().sort_index()
        sample_data_admissions = sample_data_admissions.resample("D").sum().fillna(0)

        admissions = icu.ICUAdmissions(sample_data_admissions)
        dur = durations.Durations(sample_data)
        duration_bootstrap = distributions.DurationBootstrap.from_durations(dur)
        
        n_iterations = 2
        icu_sim = icu.ICUSimulation(admissions, duration_bootstrap)
        results = icu_sim.simulate(n_iterations, show_progress=False)
        df_results = results.get_simulation_results()
        assert df_results.shape[1] == n_iterations

        results.plot.lineplot()
        plt.close()
