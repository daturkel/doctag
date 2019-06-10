from setuptools import setup

setup(
    name="doctag",
    version="0.0.2",
    description="An interface for associating objects with descriptive tags.",
    long_description=open("README.md").read(),
    install_requires=["boolean.py>=3.6", "ujson>=1.35"],
    extras_require={"test": ["pytest>=4.6", "pytest-cov>=2.7", "coveralls>=1.8.0"]},
    url="https://github.com/daturkel/doctag",
    author="Dan Turkel",
    author_email="daturkel@gmail.com",
    license="MIT",
    packages=["doctag"],
    zip_safe=False,
)
