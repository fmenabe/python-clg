# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='Command Line Generator',
    version='0.1',
    author='François Ménabé',
    author_email='francois.menabe@gmail.com',
    py_modules=['clg'],
    license='LICENCE.txt',
    description='Generate a command line parser from a structured dictionnary.',
    long_description=open('README.txt').read(),
    install_requires=[
        'argparse',
    ]
)
