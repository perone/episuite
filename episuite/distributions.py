from abc import ABC, abstractmethod
from typing import List, Optional, Union

import numpy as np


class DurationDistribution(ABC):
    """Base class for a duration distribution."""

    @abstractmethod
    def sample(self, size: int) -> np.ndarray:
        """Sample from the duration distribution.

        :param size: amount of samples to draw.
        :returns: samples from the distribution
        """
        raise NotImplementedError


class EmpiricalBootstrap(DurationDistribution):
    """This distribution will bootstrap from an empirical
    distribution.

    :param replace: if sample w/ replacement or not
    """
    def __init__(self, samples: Union[List[int], np.ndarray],
                 replace: bool = True):
        self.samples = np.asarray(samples)
        self.replace = replace

    def sample(self, size: Optional[int] = None) -> np.ndarray:
        """Sample from the duration distribution.

        :param size: amount of samples to draw.
        :returns: samples from the distribution
        """
        size = size or len(self.samples)
        samples = np.random.choice(self.samples,
                                   size=size,
                                   replace=self.replace)
        return samples
