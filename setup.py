#!/usr/bin/env python3
"""
Setup script for PyCluster
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pycluster",
    version="0.1.0",
    author="PyCluster Team",
    author_email="team@pycluster.dev",
    description="Distributed parallel execution across LAN devices",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pycluster/pycluster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "pycluster=pycluster.cli:main",
        ],
    },
    keywords="distributed computing parallel execution cluster lan",
    project_urls={
        "Homepage": "https://github.com/krishnasharma0101/pycluster",
        "Documentation": "https://pycluster.readthedocs.io/",
        "Repository": "https://github.com/krishnasharma0101/pycluster",
        "Bug Tracker": "https://github.com/krishnasharma0101/pycluster/issues",
        "Source Code": "https://github.com/krishnasharma0101/pycluster",
    },
) 