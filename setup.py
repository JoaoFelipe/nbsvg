#!/usr/bin/env python

from distutils.core import setup

setup(
    python_requires = '>=3.7',
    install_requires=[
        "lxml",
        "pygments",
        "Pillow",
        "imgkit",
        'mistune',
    ],
)