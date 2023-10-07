from setuptools import setup, find_packages

setup(
    name='LogParse',
    author = 'Ben Mackereth',
    version='0.1',
    packages=find_packages(include=['LogParse']),
    install_requires=['re','dpkt','socket']
)