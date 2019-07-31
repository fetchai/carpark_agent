# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

import subprocess
import sys
import distutils

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


print("platform: " + sys.platform)
print("platform: " + distutils.util.get_platform())


# subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', '{0}'.format("requirements_osx.txt")])


#
# setup(
#     name='carpark_agent',
#     version='0.1.0',
#     description='Fetch.AI parking space detection agent to run on Raspberry Pi',
#     long_description=readme,
#     author='Diarmid Campbell',
#     author_email='diarmid.campbell@fetch.ai',
#     url='https://github.com/fetchai/carpark_agent',
#     license=license,
#     packages=find_packages()
# )

