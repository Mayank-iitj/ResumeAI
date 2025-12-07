"""
Setup script for Resume Analyzer CLI
Created by: MAYANK SHARMA
Website: https://mayankiitj.vercel.app
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="resume-analyzer-cli",
    version="1.0.0",
    author="MAYANK SHARMA",
    author_email="202410104+Mayank-iitj@users.noreply.github.com",
    description="Production-ready CLI tool for resume analysis and ATS scoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mayank-iitj/ResumeAI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "resume-analyzer=analyzer:main",
        ],
    },
)
