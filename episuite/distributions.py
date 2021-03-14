from abc import ABC, abstractmethod
from typing import List, Optional, Union

import numpy as np

from episuite.durations import Durations


class DurationDistribution(ABC):
    """Base class for a duration distribution."""

    @abstractmethod
    def sample(self, size: int) -> np.ndarray:
        """Sample from the duration distribution.

        :param size: amount of samples to draw.
        :returns: samples from the distribution
        """
        raise NotImplementedError


class DurationBootstrap(DurationDistribution):
    """This distribution will bootstrap a specified list
    of durations.

    :param replace: if sample w/ replacement or not
    """
    def __init__(self, durations: Union[List[int], np.ndarray],
                 replace: bool = True):
        self.durations = np.asarray(durations)
        self.replace = replace

    @classmethod
    def from_durations(cls, duration: Durations):
        stay_distribution: np.ndarray = duration.get_stay_distribution()
        return cls(stay_distribution)

    def sample(self, size: Optional[int] = None) -> np.ndarray:
        """Sample from the duration distribution.

        :param size: amount of samples to draw.
        :returns: samples from the distribution
        """
        size = size or len(self.durations)
        samples = np.random.choice(self.durations,
                                   size=size,
                                   replace=self.replace)
        return samples
