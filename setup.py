#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
from setuptools.command.test import test


REQUIREMENTS = (
    "six",
)


with open("README.rst", "r") as resource:
    LONG_DESCRIPTION = resource.read()


# copypasted from http://pytest.org/latest/goodpractises.html
class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = None  # pylint: disable=W0201

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []  # pylint: disable=W0201
        self.test_suite = True  # pylint: disable=W0201

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        import sys
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="isitbullshit",
    description=("Small library for verifying parsed JSONs "
                 "if they are bullshit or not"),
    long_description=LONG_DESCRIPTION,
    version="0.2.1",
    author="Sergey Arkhipov",
    license="MIT",
    author_email="serge@aerialsounds.org",
    maintainer="Sergey Arkhipov",
    maintainer_email="serge@aerialsounds.org",
    url="https://github.com/9seconds/isitbullshit/",
    install_requires=REQUIREMENTS,
    keywords="json validation jsonschema",
    tests_require=["pytest==2.6.1"],
    packages=find_packages(),
    cmdclass={'test': PyTest},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",

    ],
    zip_safe=False
)
