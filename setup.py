#!/usr/bin/env python

import re
from os.path import abspath, dirname, join
from setuptools import setup

CURDIR = dirname(abspath(__file__))
REQUIREMENTS = ["robotframework >= 7.0", "opencv-python >= 4.9.0.80", "python-vlc >= 3.0.20123", "ffmpeg-python >= 0.2.0", "numpy >= 1.23.4", "ping3 >= 4.0.8"]
with open(join(CURDIR, "src", "MulticastLibrary", "version.py")) as f:
    VERSION = re.search("\nVERSION = '(.*)'", f.read()).group(1)
with open(join(CURDIR, "README.rst")) as f:
    DESCRIPTION = f.read()
    
CLASSIFIERS = """
License :: OSI Approved :: Apache Software License
Operating System :: Linux
Programming Language :: Python
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
""".strip().splitlines()

setup(
    name="robotframework-multicastlibrary",
    version=VERSION,
    description="Robot Framework multicast library for ffmpeg, vlc and cv2",
    long_description=DESCRIPTION,
    author="Ganesan Selvaraj",
    author_email="ganesanluna@yahoo.in",
    url="https://github.com/ganesanluna/MulticastLibrary",
    license="Apache License 2.0",
    keywords="robotframework testing testautomation",
    platforms="linux",
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    package_dir={"": "src"},
    packages=["MulticastLibrary"],
)
