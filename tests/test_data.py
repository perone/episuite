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

    def test_load_from_cache(self) -> None:
        fname = "cache_test.txt"
        cache_file = data.get_cache_dir_file(fname)
        assert cache_file.exists() is False

        fcache = data.load_from_cache(self.MOCK_URL_TEST,
                                      fname, show_progress=False)
        assert fcache.exists()
        mtime_cached = fcache.stat().st_mtime

        # Download again and check if it has not modified cached file
        fcache_again = data.load_from_cache(self.MOCK_URL_TEST,
                                            fname, show_progress=False)
        mtime_cached_again = fcache_again.stat().st_mtime
        assert mtime_cached_again == mtime_cached

        fcache.unlink()
        assert not fcache.exists()
        assert not fcache_again.exists()
