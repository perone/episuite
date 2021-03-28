import episuite


class TestMain:
    def test_one(self) -> None:
        assert episuite.__version__ is not None
        assert episuite.__author__ is not None
        assert episuite.__appname__ is not None
