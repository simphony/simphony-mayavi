import os

from setuptools import setup, find_packages

with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()

VERSION = '0.0.1dev'


def write_version_py(filename=None):
    if filename is None:
        filename = os.path.join(
            os.path.dirname(__file__), 'simphony_mayavi', 'version.py')
    ver = """\
version = '%s'
"""
    fh = open(filename, 'wb')
    try:
        fh.write(ver % VERSION)
    finally:
        fh.close()


write_version_py()

setup(
    name='simphony_mayavi',
    version=VERSION,
    author='SimPhoNy FP7 European Project',
    description='The mayavi visualisation plugin for SimPhoNy',
    long_description=README_TEXT,
    install_requires=[
        "simphony-common",
        "mayavi"],
    packages=find_packages(),
    entry_points={
        'simphony.visualisation': ['mayavi = simphony_mayavi.api']})
