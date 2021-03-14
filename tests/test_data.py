from episuite import data


class TestSampleData:
    def test_dt_columns(self) -> None:
        ret = data.admissions_sample()
        assert len(ret) == 4538
        assert ret.shape[1] == 3
