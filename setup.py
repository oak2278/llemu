from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="llemu",
    version="0.1.0",
    author="LLEMU Team",
    author_email="info@llemu.dev",
    description="LLM-Enhanced ROM Management Utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llemu/llemu",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "llemu=llemu.__main__:main",
        ],
    },
    include_package_data=True,
)
