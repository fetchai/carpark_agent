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



subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pillow'])
subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'setuptools'])
subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'wheel'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'numpy < 1.17'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'adafruit-circuitpython-gps == 3.3.0'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'gps == 3.19'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'colour'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'IPython'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'h5py'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'tablib'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'crontab'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'clint'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'docopt'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'Cython'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'coco == 0.4.0'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'pycocotools'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'tensorflow == 1.13.1'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'keras == 2.2.4'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'oef == 0.4.0'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'fetchai-ledger-api == 0.5.1'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'base58'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'pywt'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'shapely == 1.6.4.post2', '--no-dependencies'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'scikit-image == 0.15.0', '--no-dependencies'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'imgaug == 0.2.9', '--no-dependencies'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'imageio == 2.5.0', '--no-dependencies'])


#
#
# platform = distutils.util.get_platform()
# print("platform: " + platform)
#
# # If raspberry Pi, 3 or 4
# if platform == "linux-armv7l":
#     subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_rpi.txt', '--no-dependencies'])
# # If  mac
# elif platform.startswith("macosx"):
#     subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_osx.txt', '--no-dependencies'])
# else:
#     print("Error unsupported platform")
#     exit()

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

