# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re

from setuptools import setup

version = re.search(
    r"^__version__\s*=\s*'(.*)'",
    open('tav/tav.py').read(),
    re.M
).group(1)


setup(
    name='tav',
    packages=['tav'],
    entry_points={
        "console_scripts": ['tav = tav.tav:main']},
    version=version,
    description='TBD',
    long_description='TBD',
    author='Mudox',
    author_email='imudox@gmail.com',
    url='https://github.com/mudox/tav'
)
