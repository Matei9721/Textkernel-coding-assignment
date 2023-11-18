from setuptools import setup, find_packages

setup(
    name="country_matcher",
    version="1.0",
    packages=find_packages(),
    install_requires=["thefuzz"]
)
