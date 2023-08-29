from setuptools import setup, find_packages

setup(
    name='TSS_Python',
    author = 'Ben Mackereth',
    version='0.1',
    packages=find_packages(include=['Modules/TSS_Python']),
    install_requires=['requests']
)