# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='clg',
    version='0.2',
    author='François Ménabé',
    author_email='francois.menabe@gmail.com',
    py_modules=['clg'],
    license='LICENSE.txt',
    description='Command-line generator from a dictionary.',
    long_description=open('README').read(),
    install_requires=[
        'argparse',
    ]
)
