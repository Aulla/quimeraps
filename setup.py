"""Main setup script."""

import setuptools  # type: ignore
import pathlib
import subprocess
from . import json_srv


with open("requirements.txt") as f:
    required = f.read().splitlines()

version_ = json_srv.__VERSION__

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quimeraps",
    version=version_,
    author="José A. Fernández Fernández",
    author_email="aullasistemas@gmail.com",
    description="Quimera Print Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    package_data={
        "quimera-ps.client_gui": ["*"],
    },
    install_requires=required,
    keywords="eneboo pineboo printer json",
    python_requires=">=3.6.9",
    entry_points={
        "console_scripts": [
            "quimera_service=quimera_ps.service:startup",
            "quimera_client=quimera_ps.client.startup",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Typing :: Typed",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
    ],
)
