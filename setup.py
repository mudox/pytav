# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""

import re

from setuptools import find_packages, setup

version = re.search(
    r"^__version__\s*=\s*'(.*)'",
    open('src/tav/cmd.py').read(), re.M
).group(1)

setup(
    name='tav',
    version=version,
    description='TBD',
    long_description='TBD',
    author='Mudox',
    author_email='imudox@gmail.com',
    url='https://github.com/mudox/tav',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'libtmux',
        'ruamel.yaml',
    ],
    package_data={
        '': ['resources/*'],
    },
    scripts=[
        'assets/scripts/tavs',
    ],
    entry_points={
        "console_scripts": ['tav = tav.cmd:run']
    }
)
