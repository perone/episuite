import pytest
from episuite.mobility import facebook


class TestFacebookSurvey:
    def test_country_region(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_country_region()
        item = result[0]
        assert "country" in item.keys()
        assert "region" in item.keys()

    def test_survey_date_avail(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_date_avail("Brazil",
                                         "Rio Grande do Sul")
        item = result[0]
        assert set(["country", "region",
                    "survey_date"]).issubset(item.keys())

    def test_get_survey_range(self) -> None:
        c = facebook.FacebookSymptomSurvey()
        result = c.get_survey_range("Brazil", "Rio Grande do Sul",
                                    "20210101", "20210105")
        assert len(result) == 5


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
