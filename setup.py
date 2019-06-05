from setuptools import setup

setup(
    name="doctag",
    version="0.0.1",
    description="An interface for associating objects with descriptive tags.",
    long_description=open("README.txt").read(),
    install_requires=["boolean.py>=3.6", "ujson>=1.35"],
    url="https://github.com/daturkel/doctag",
    author="Dan Turkel",
    author_email="daturkel@gmail.com",
    license="MIT",
    packages=["doctag"],
    zip_safe=False,
)
