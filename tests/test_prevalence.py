import numpyro
import pytest

numpyro.set_host_device_count(2)
from jax import random
#import arviz as az
from numpyro.infer import MCMC, NUTS, init_to_feasible

from episuite import prevalence


class TestTruePrevalenceModel:
    def test_half_prevalence(self) -> None:
        num_warmup, num_samples = 100, 500
        rng_key = random.PRNGKey(42)
        rng_key, rng_key_ = random.split(rng_key)

        kernel = NUTS(prevalence.true_prevalence_model,
                      init_strategy=init_to_feasible())
        mcmc = MCMC(kernel, num_warmup, num_samples, num_chains=1,
                    progress_bar=False)
        mcmc.run(rng_key_, obs_positive=500, obs_total=1000)
        samples = mcmc.get_samples()

        true_p = samples["true_p"].mean()
        assert true_p == pytest.approx(0.5, rel=0.1)


class TestApparentPrevalenceModel:
    def test_half_prevalence(self) -> None:
        n_sp = 100
        x_sp = 100
        n_se = 100
        x_se = 100

        obs_total = 1000
        obs_positive = 500

        num_warmup, num_samples = 100, 500
        rng_key = random.PRNGKey(42)
        rng_key, rng_key_ = random.split(rng_key)

        kernel = NUTS(prevalence.apparent_prevalence_model,
                      init_strategy=init_to_feasible())
        mcmc = MCMC(kernel, num_warmup,
                    num_samples, num_chains=1,
                    progress_bar=False)
        mcmc.run(rng_key_, x_se=x_se, n_se=n_se,
                 x_sp=x_sp, n_sp=n_sp,
                 obs_positive=obs_positive,
                 obs_total=obs_total)
        
        samples = mcmc.get_samples()
        true_p = samples["true_p"].mean()
        assert true_p == pytest.approx(0.5, rel=0.1)
