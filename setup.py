# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in contentready_oip/__init__.py
from contentready_oip import __version__ as version

setup(
	name='contentready_oip',
	version=version,
	description='Open Innovation Platform',
	author='ContentReady',
	author_email='hello@contentready.co',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
