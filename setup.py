from typing import List

import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

development_requires: List[str] = [
    "pytest>=6.2.2",
    "mypy>=0.812",
    "flake8>=3.8.4",
    "pytest-cov>=2.11.1",
    "sphinx>=3.5.2",
    "pydata-sphinx-theme>=0.5.0",
    "sphinx-tabs>=2.1.0",
    "nbsphinx>=0.8.2",
    "ipykernel>=5.5.0",
    "isort>=5.7.0",
    "invoke>=1.5.0",
    "pydocstyle>=5.1.1",
    "twine>=3.3.0",
    "sphinx-autobuild>=2021.3.14",
    "ipywidgets>=7.6.3",
]

setuptools.setup(
    name="episuite",
    version="0.1.0",
    author="Christian S. Perone",
    author_email="christian.perone@gmail.com",
    description="A suite of tools for epidemiology in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perone/episuite",
    install_requires=[
        "numpy>=1.20.1",
        "matplotlib>=3.3.4",
        "pandas>=1.2.3",
        "pymc3>=3.11.1",
        "seaborn>=0.11.1",
        "tqdm>=4.59.0",
    ],
    extras_require={
        'dev': development_requires,
    },
    project_urls={
        "Bug Tracker": "https://github.com/perone/episuite/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "episuite": ["sample_data/*.csv"],
    }
)
