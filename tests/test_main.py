import unittest

import episuite


class TestMain(unittest.TestCase):
    def test_one(self) -> None:
        _ = episuite.__version__
        self.assertTrue(1 == 1)
