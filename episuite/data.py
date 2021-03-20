from pathlib import Path
from typing import BinaryIO, Optional, Union

import pandas as pd
import pkg_resources
import requests
from appdirs import AppDirs
from tqdm.auto import tqdm

import episuite


def get_cache_dir_file(filename: Optional[Union[str, Path]] = None) -> Path:
    dirs = AppDirs(episuite.__appname__,
                   episuite.__author__,
                   version=episuite.__version__)
    cache_dir = Path(dirs.user_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    if filename is not None:
        cache_dir = cache_dir / Path(filename)
    return cache_dir


def load_from_cache(url: str, filename: Union[str, Path],
                    desc: Optional[str] = None,
                    show_progress: bool = True) -> Path:
    cache_dir = get_cache_dir_file()
    filename_output = cache_dir / Path(filename)

    # Already exists in the cache
    if filename_output.exists():
        return filename_output

    with filename_output.open(mode="wb") as fhandle:
        download_remote(url, fhandle, desc, show_progress)

    return filename_output


def download_remote(url: str, stream: BinaryIO,
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
    """Sample data for ICU hospitalization admissions. This data is based
    on COVID-19 outbreak in Porto Alegre/RS/Brazil. This dataset contains
    three columns that are described below.

    DATE_START
        When the patient enters in the ICU.

    DATE_END
        When the patient left the ICU by an outcome.

    OUTCOME
        Outcome when the patient left the ICU (DATE_END)

    :returns: sample data w/ admission
    """
    sample_fname = \
        pkg_resources.resource_filename(__name__, "sample_data/admission_sample.csv")
    df = pd.read_csv(sample_fname, parse_dates=["DATE_START", "DATE_END"])
    return df
