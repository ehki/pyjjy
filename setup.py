from setuptools import setup, find_packages
from codecs import open

import pyjjy

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyjjy',
    version=pyjjy.__version__,
    url='http://pypi.python.org/pypi/pyjjy/',
    author='Haruki EJIRI',
    author_email='0y35.ejiri.vmqewyhw@gmail.com',
    description='JJY signal emulator using python and pyaudio',
    license='MIT',
    python_requires='>=3.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['PyAudio>=0.2.11'],
    long_description=long_description,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)