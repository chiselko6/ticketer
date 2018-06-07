#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='Ticketer',
      version='0.1',
      author='chiselko6',
      author_email='alex.limontov@gmail.com',
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'ticketer=app.cli:start',
        ]
    }
)
