#!/usr/bin/python3
import glob
import os

from setuptools import setup

import pushserver.__info__ as package_info

long_description = """
Sylk Pushserver was designed to act as a central dispatcher for mobile push
notifications inside RTC provider infrastructures.  Both the provider and
the mobile application customer, in the case of a shared infrastructure, can
easily audit problems related to the processing of push notifications. 
"""

def find_packages(root):
    return [directory.replace(os.path.sep, '.') for directory, sub_dirs, files in os.walk(root) if '__init__.py' in files]

def requirements():
    install_requires = []
    with open('requirements.txt') as f:
        for line in f:
            install_requires.append(line.strip())
    return install_requires


setup(name=package_info.__project__,
      version=package_info.__version__,
      description=package_info.__summary__,
      long_description=long_description,
      author=package_info.__author__,
      license=package_info.__license__,
      platforms=['Platform Independent'],
      author_email=package_info.__email__,
      url=package_info.__webpage__,
      scripts=['sylk-pushserver', 'scripts/sylk-pushclient', 'scripts/sylk-pushclient-v2', 'scripts/sylk-pushserver-db'],
      packages=find_packages('pushserver'),
      # install_requires=requirements(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Service Providers',
          'License :: GPL v3',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      data_files=[('/etc/sylk-pushserver', []),
                  ('/etc/sylk-pushserver', glob.glob('config/*.sample')),
                  ('/etc/sylk-pushserver/credentials', []),
                  ('/etc/sylk-pushserver/applications',
                   glob.glob('config/applications/*.py')),
                  ('/etc/sylk-pushserver/applications/app_template',
                   glob.glob('config/applications/app_template/*.py')),
                  ('/var/log/sylk-pushserver', [])]
      )
