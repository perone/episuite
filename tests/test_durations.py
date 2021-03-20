import pandas as pd
import pytest
from matplotlib import pyplot as plt

from episuite.durations import Durations


class TestDurations:
    @pytest.fixture
    def mock_duration(self) -> pd.DataFrame:
        start_date = pd.date_range("2020-01-01", "2020-01-10")
        end_date = pd.date_range("2020-01-11", "2020-01-20")
        return pd.DataFrame({
            "DATE_START": start_date,
            "DATE_END": end_date
        })

    def test_dt_columns(self, mock_duration: pd.DataFrame) -> None:
        dur = Durations(mock_duration)

    def test_dt_columns_error(self, mock_duration: pd.DataFrame) -> None:
        mock_duration.columns = ["a", "b"]
        with pytest.raises(ValueError, match="dataframe should have"):
            _ = Durations(mock_duration)

    def test_get_stay_distribution(self, mock_duration: pd.DataFrame) -> None:
        dur = Durations(mock_duration)
        distr = dur.get_stay_distribution()
        assert len(distr) == 10
        assert (distr==10).all()

    def test_plot(self, mock_duration: pd.DataFrame) -> None:
        dur = Durations(mock_duration)

        dur.plot.density()
        plt.close()

        dur.plot.histogram()
        plt.close()

        dur.plot.timeplot()
        plt.close()
