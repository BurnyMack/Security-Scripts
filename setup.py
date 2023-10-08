from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='modules',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
    author='Ben Mackereth',
    url='https://github.com/BurnyMack',
)
