#!/usr/bin/env python
# setup script for arm_archive

from distutils.core import setup

setup(
    name='arm_archive',
    version='0.1.0',
    author='Jonathan J. Helmus',
    author_email='jjhelmus@gmail.com',
    py_modules=['arm_archive'],
    license='BSD',
    url='https://github.com/jjhelmus/arm_archive',
    description='A module for accessing data from the ARM Archive',
    long_description=open('README.rst').read(),
    requires=['suds'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
    ]
)
