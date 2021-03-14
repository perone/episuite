import pandas as pd
import pkg_resources


def admissions_sample():
    sample_fname = \
        pkg_resources.resource_filename(__name__, "sample_data/admission_sample.csv")
    df = pd.read_csv(sample_fname, parse_dates=["DATE_START", "DATE_END"])
    return df
