#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

tests_require = ['nose', 'mock', 'responses', 'flake8']

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup(
    name="ironSourceAtom",
    version="1.0.0",
    description="ironSource.atom Python SDK",
    packages=["ironSourceAtom"],
    author="ironSource.atom",
    author_email="atom@ironsrc.com",
    url="https://github.com/ironSource/atom-python",
    tests_require=tests_require,
    test_suite='nose.collector',
    license='MIT',
    install_requires=reqs,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
