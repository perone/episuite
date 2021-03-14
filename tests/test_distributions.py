import numpy as np
import pytest

from episuite import distributions


class TestDurationBootstrap:
    def test_sample(self) -> None:
        ones = np.ones(100, dtype=np.int32)
        dist = distributions.DurationBootstrap(ones)
        samples = dist.sample(100)
        assert (samples==1).sum() == 100
