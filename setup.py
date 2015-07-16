#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='capsule_api',
      description='Simple python library for the CapsuleCRM API',
      version='0.1',
      packages=find_packages(),
      install_requires=['requests==2.7.0']
      )
