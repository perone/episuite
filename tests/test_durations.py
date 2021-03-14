import pandas as pd
import pytest
from matplotlib import pyplot as plt

from episuite.durations import Durations


class TestDurations:
    @pytest.fixture
    def mock_duration(self) -> pd.DataFrame:
        start_data = pd.date_range("2020-01-01", "2020-01-10")
        end_data = pd.date_range("2020-01-11", "2020-01-20")
        return pd.DataFrame({
            Durations.COLUMN_START: start_data,
            Durations.COLUMN_END: end_data
        })

    def test_dt_columns(self, mock_duration) -> None:
        dur = Durations(mock_duration)

    def test_dt_columns_error(self, mock_duration) -> None:
        mock_duration.columns = ["a", "b"]
        with pytest.raises(ValueError, match="dataframe should have"):
            _ = Durations(mock_duration)

    def test_get_stay_distribution(self, mock_duration) -> None:
        dur = Durations(mock_duration)
        distr = dur.get_stay_distribution()
        assert len(distr) == 10
        assert (distr==10).all()

    def test_plot(self, mock_duration) -> None:
        dur = Durations(mock_duration)

        dur.plot.density()
        plt.close()

        dur.plot.histogram()
        plt.close()

        dur.plot.timeplot()
        plt.close()
