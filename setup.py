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



platform = distutils.util.get_platform()
print("platform: " + platform)

# If raspberry Pi, 3 or 4
if platform == "linux-armv7l":
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_rpi4.txt'])
# If raspberry mac
elif platform.startswith("macosx"):
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_osx.txt'])
else:
    print("Error unsupported platform")
    exit()

setup(
    name='carpark_agent',
    version='0.1.0',
    description='Fetch.AI parking space detection agent to run on Raspberry Pi',
    long_description=readme,
    author='Diarmid Campbell',
    author_email='diarmid.campbell@fetch.ai',
    url='https://github.com/fetchai/carpark_agent',
    license=license,
    packages=find_packages(),
    package_data={'': ['mask_rcnn_coco.h5', 'default_mask_ref.png']},
    include_package_data=True,

)

