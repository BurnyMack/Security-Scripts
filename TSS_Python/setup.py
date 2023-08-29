from setuptools import setup, find_packages

setup(
    name='TSS_Python',
    author = 'Ben Mackereth',
    version='0.1',
    packages=find_packages(include=['TSS_Python']),
    install_requires=['requests']
)