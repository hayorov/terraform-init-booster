import os
import setuptools

from pathlib import Path

with open(Path(f"{os.path.dirname(os.path.realpath(__file__))}/README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tf-init-booster",
    version="1.0.0",
    author="Alex Khaerov",
    description="terraform init booster",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["tf-init-booster=tf_init_booster.booster:main"],},
)
