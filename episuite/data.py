import io
from typing import Optional

import pandas as pd
import pkg_resources
import requests
from tqdm.auto import tqdm


def download_remote(url: str, stream: io.BufferedIOBase,
                    desc: Optional[str] = None,
                    show_progress: bool = True) -> None:
    """This function will download data frmo a remote URL and
    will optionally show the progress.

    :param url: the url to download from
    :param stream: buffered IO object
    :param desc: progress bar description
    :param show_progress: whether to show progress or not
    """
    resp = requests.get(url, stream=True)
    content_length = resp.headers.get('content-length', 0)
    total = int(content_length)
    with tqdm(desc=desc, total=total, unit='iB', unit_scale=True,
              unit_divisor=1024, disable=not show_progress) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = stream.write(data)
            bar.update(size)


def admissions_sample() -> pd.DataFrame:
    """Sample data for hospitalization admissions. This data is based
    on COVID-19 outbreak in Porto Alegre/RS/Brazil.

    :returns: sample data w/ admission
    """
    sample_fname = \
        pkg_resources.resource_filename(__name__, "sample_data/admission_sample.csv")
    df = pd.read_csv(sample_fname, parse_dates=["DATE_START", "DATE_END"])
    return df
