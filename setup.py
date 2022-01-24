from setuptools import setup
import os

setup(
    name='Watchdog',
    packages=['watchdog'],
    version='0.0.1',
    description='Python bindings for MbientLab\'s Warble library',
    author='Murray Tait',
    author_email="tait.mw@gmail.com",
    keywords = ['watchdog'],
    python_requires='>=3.7',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ]
)
