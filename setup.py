import io
import setuptools
from setuptools import setup


setup(
    name="aep_parser",
    version="0.0.2",
    author="Benoit Delaunay",
    author_email="delaunay.ben@gmail.com",
    description="A .aep (After Effects Project) parser",
    long_description=io.open("readme.md", mode="r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: File Formats",
        "Topic :: Multimedia :: Graphics",
    ],
    install_requires=[
        "kaitaistruct>=0.9",
        "enum34 ; python_version<'3.4'",
        "future ; python_version<'3.0'",
        "six ; python_version<'3.0'",
    ],
    python_requires=">=2.7",
    options={"bdist_wheel": {"universal": True}},
)
