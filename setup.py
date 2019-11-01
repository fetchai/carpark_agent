# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

import subprocess
import sys
import os
import distutils

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

platform = distutils.util.get_platform()
print("platform: " + platform)



if platform.startswith("macosx"):
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'scipy'])
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'scikit-image'])
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'scikit-learn'])
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'ipython'])
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'pandas'])
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'opencv-python'])



subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pillow'])
subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'setuptools'])
subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'wheel'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'numpy < 1.17'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'adafruit-circuitpython-gps == 3.3.0'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'adafruit-blinka == 2.2.0'])
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
subprocess.call([sys.executable, '-m', 'pip', 'install', 'aea'])

if platform.startswith("win32"):
    pass
    #subprocess.call(['rm', '-rf', './_win/'])
    #subprocess.call(['git', 'clone', 'git@github.com:philferriere/cocoapi.git', './_win/cocoapi'])
    #currentdir = os.getcwd()
    #os.chdir('_win/cocoapi/PythonAPI')
    #subprocess.call([sys.executable, 'setup.py', 'install'])
    #os.chdir(currentdir )
else:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'pycocotools'])

if platform.startswith("win32"):
    pass
    #subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.13.1-py3-none-any.whl'])
else:
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'tensorflow == 1.13.1'])

subprocess.call([sys.executable, '-m', 'pip', 'install', 'keras == 2.2.4'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'pywt'])
if not platform.startswith("win32"):
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'shapely == 1.6.4.post2', '--no-dependencies'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'scikit-image == 0.15.0', '--no-dependencies'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'imgaug == 0.2.9', '--no-dependencies'])
subprocess.call([sys.executable, '-m', 'pip', 'install', 'imageio == 2.5.0', '--no-dependencies'])


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
    include_package_data=True
)

