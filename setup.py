#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'pioo'

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='libncore',
      version='0.1',
      description='ncore library for python',
      url='http://github.com/piooca/libncore',
      author='piooca',
      author_email='pioo84@gmail.com',
      license='MIT',
      packages=['libncore'],
      install_requres=[
            'sqlite3',
            'transmissionrpc',
            'bs4',
            'ConfigParser',
      ],
      include_package_data=True,
      entry_points = {
            'console_scripts': ['ncore_util=libncore.cmd_ncore_util:main',
                                'ncore_figyelo=libncore.cmd_ncore_figyelo:main'],
      },
      zip_safe=False)

