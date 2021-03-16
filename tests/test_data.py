import io
import json
from pathlib import Path

from episuite import data


class TestSampleData:
    def test_dt_columns(self) -> None:
        ret = data.admissions_sample()
        assert len(ret) == 4538
        assert ret.shape[1] == 3

class TestUtils:
    MOCK_URL_TEST: str = "http://echo.jsontest.com/episuite/test"
    def test_download_remote(self) -> None:
        with io.BytesIO() as stream:
            data.download_remote(self.MOCK_URL_TEST, stream,
                                 show_progress=False)
            value = stream.getvalue()
        json_decoded = json.loads(value)
        assert "episuite" in json_decoded
