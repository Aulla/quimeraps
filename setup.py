"""Main setup script."""

import setuptools  # type: ignore
from quimeraps import __VERSION__


with open("requirements.txt") as f:
    required = f.read().splitlines()

version_ = __VERSION__

with open("README", "r") as fh:
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
    package_data={"quimeraps.client_gui": ["*.ui"]},
    install_requires=required,
    keywords="eneboo pineboo printer json",
    python_requires=">=3.6.9",
    entry_points={
        "console_scripts": [
            "quimeraps_server=quimeraps.entry_points:startup_server",
            "quimeraps_client=quimeraps.entry_points:startup_client",
            "quimeraps_daemon=quimeraps.entry_points:install_daemon",
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
