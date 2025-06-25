#!/usr/bin/env python3
"""
Setup script for Bitcoin Balance Tracker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bitcoin-balance-tracker",
    version="1.0.0",
    author="Bitcoin Balance Tracker",
    description="A Python application that tracks Bitcoin wallet balances using a local Bitcoin Core pruned node",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bitcoin-balance-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bitcoin-tracker=bitcoin_tracker:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 