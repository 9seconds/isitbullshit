#!/usr/bin/env python
# -*- coding: utf-8 -*-


# #############################################################################


from setuptools import setup


# #############################################################################


setup(
    name='isitbullshit',
    version='0.1.0',
    url='https://github.com/9seconds/isitbullshit',
    license='MIT',
    author='Sergey Arkhipov',
    author_email='serge@aerialsounds.org',
    description='Library to help with matching between JSON and simple schema',
    long_description=__doc__,
    py_modules=['isitbullshit'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
    ]
)
