#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://funimationlater.rtfd.org."""

history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='funimationlater',
    version='0.0.1',
    description='A Python library for the Funimation Now API',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Aaron Frase',
    author_email='afrase91@gmail.com',
    url='https://github.com/Sinap/funimationlater',
    packages=[
        'funimationlater',
    ],
    package_dir={'funimationlater': 'funimationlater'},
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords='funimationlater',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
