from typing import Any
import numpyro
import numpyro.distributions as dist

from numpyro.distributions import Distribution


def true_prevalence_model(obs_positive: int, obs_total: int,
                          true_p_prior: Distribution = dist.Beta(1, 1)) -> Any:
    """This is a true prevalence model, which means that it will assume
    for instance perfect testing validation results if it is a
    seroprevalence study.

    :param obs_positive: number of observed positive counts
    :param obs_total: the total of observed samples
    :param true_p_prior: it can be any numpyro distribution to use as prior
                         for the true prevalence (default to a flat Beta prior)
    """
    true_p = numpyro.sample("true_p", true_p_prior)
    binomial_dist = dist.Binomial(total_count=obs_total, probs=true_p)
    return numpyro.sample("obs", binomial_dist, obs=obs_positive)


def apparent_prevalence_model(x_se: int, n_se: int,
                              x_sp: int, n_sp: int,
                              obs_total: int,
                              obs_positive: int,
                              true_p_prior: Distribution = dist.Beta(1, 1)) -> Any:
    """This is a more realistic model that takes into consideration a imperfect
    testing validation, and uses the Rogan-Gladen estimator to model the observed
    prevalence as an apparent prevalence.

    .. seealso::

        `Estimating SARS-CoV-2 seroprevalence and epidemiological parameters with uncertainty from serological surveys <https://www.medrxiv.org/content/10.1101/2020.04.15.20067066v2>`_
            This is mostly based on the work :cite:t:`Larremore2020`.

        `Analysis of the SARS-CoV-2 outbreak in Rio Grande do Sul / Brazil <https://arxiv.org/abs/2007.10486>`_
            This article :cite:t:`perone2020analysis` used this simulator and describes how it works.

    :param x_se: sensitivity parameter (i.e. if there was 33 positive samples, and
                 27 were detected, this parameter is 27).
    :param n_se: sensitivity parameter (i.e. if there was 33 positive samples, and
                 27 were detected, this parameter is 33).
    :param x_sp: specificity parameter (i.e. if 172 negative tests, there was 2 false
                 positives, this parameter is 170).
    :param n_sp: specificity parameter (i.e. if 172 negative tests, there was 2 false
                 positives, this parameter is 172).
    :param obs_positive: number of observed positive counts
    :param obs_total: the total of observed samples
    :param true_p_prior: it can be any numpyro distribution to use as prior
                         for the true prevalence (default to a flat Beta prior)
    """
    true_p = numpyro.sample("true_p", true_p_prior)
    se_p = numpyro.sample("se_p", dist.Beta(x_se + 1, n_se - x_se + 1))
    sp_p = numpyro.sample("sp_p", dist.Beta(x_sp + 1, n_sp - x_sp + 1))
    apparent_p = numpyro.deterministic("apparent_p",
                                       true_p * se_p + (1.0 - true_p) * (1.0 - sp_p))
    return numpyro.sample("obs",
                          dist.Binomial(probs=apparent_p,
                                        total_count=obs_total),
                          obs=obs_positive)
