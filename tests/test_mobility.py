import pytest
from matplotlib import pyplot as plt

from episuite.mobility import facebook


class TestFacebookSurvey:
    def test_country_region(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_country_region()
        cset = set(result.columns)
        assert cset.issubset(["country", "region"])
        assert len(cset) > 0

    def test_survey_date_avail(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_date_avail("Brazil",
                                         "Rio Grande do Sul")
        cset = set(result.columns)
        assert cset.issubset(["country", "region", "survey_date"])
        assert len(cset) > 0

    def test_get_survey_range(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_range("Brazil", "Rio Grande do Sul",
                                    "20210101", "20210105")
        assert len(result) == 5

    def test_plot_region_percent_cli(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_range("Brazil", "Rio Grande do Sul",
                                    "20210101", "20210105")
        c.plot_region_percent_cli(result)
        plt.close()


class TestFacebookMovementRange:
    def test_last_date_avail(self) -> None:
        mrange = facebook.FacebookMovementRange()
        resource = mrange._get_last_date_available()
        assert "data.humdata.org" in resource.url
        assert resource.date is not None
        assert resource.filename is not None

    def test_download_resource(self) -> None:
        mrange = facebook.FacebookMovementRange()
        resource = mrange._get_last_date_available()
        cached_file = mrange._download_cache_resource(resource, False)
        assert cached_file.exists()

    @pytest.mark.slow
    def test_load_movement_range(self) -> None:
        mrange = facebook.FacebookMovementRange()
        df_bra = mrange.load_movement_range(country_code="BRA")
        df_total = mrange.load_movement_range()
        assert len(df_total) > len(df_bra)
