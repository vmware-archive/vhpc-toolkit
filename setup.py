# coding=utf-8
"""vhpc_toolkit: a toolkit for virtualized high performance computing
"""
from codecs import open
from os import path

from setuptools import find_packages
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README.md file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vhpc_toolkit",
    version="0.2.0",
    description="A toolkit for virtualized high performance computing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vmware/vhpc-toolkit",
    author="Na Zhang",
    author_email="nkuzhangna@gmail.com",
    license="Apache 2.0",
    keywords="virtualization, vSphere, high performance computing, GPU, vGPU, " "RDMA",
    packages=find_packages(exclude=["docs"]),
    python_requires=">=3",
    include_package_data=True,
    package_data={"vhpc_toolkit": ["bin/*", "config/*", "examples/*"]},
    install_requires=[
        "configparser==3.5.0",
        "pyvim==0.0.20",
        "pyvmomi>=6.5",
        "PyYAML==5.4",
        "texttable==0.8.8",
        "textwrap3==0.9.1",
        "hvac>=0.10.5",
        "coloredlogs>=15.0.1" "colorama==0.4.5",
    ],
)
