import io
import setuptools
from setuptools import setup

setup(
    name="aep_parser",
    version="0.0.1",
    author="Benoit Delaunay",
    author_email="delaunay.ben@gmail.com",
    description="A .aep (After Effects Project) parser",
    long_description=io.open("README.md", "r", "utf-8").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: File Formats",
        "Topic :: Multimedia :: Graphics",
    ],
    install_requires=[
        "kaitaistruct>=0.9",
    ],
    python_requires=">=2.7",
)