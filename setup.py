import codecs
import os.path
import pathlib

import pkg_resources
from setuptools import setup, find_packages


def read(rel_path: str) -> str:
    """
    read a text file by the relative path to the dir containing this file
    :param rel_path:
    :return:
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    """
    read version description
    :param rel_path:
    :return:
    """
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def parse_requirements(path):
    with pathlib.Path(path).open() as requirements_txt:
        install_requires = [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_requires


setup(
    name='pyprof',
    version=get_version('pyprof/__init__.py'),
    description="This package focus on build time profiler for python functions and snippets.",
    author='Zeyan Li',
    author_email='li_zeyan@icloud.com',
    url='https://github.com/lizeyan/pyprof',
    packages=find_packages(),
    project_urls={
        "Bug Tracker": "https://github.com/lizeyan/pyprof/issues",
        "Source Code": "https://github.com/lizeyan/pyprof",
        "Documentation": "https://pyprof.lizeyan.me",
    },
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
)
