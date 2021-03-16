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
