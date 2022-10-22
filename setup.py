from setuptools import setup, find_packages

setup(
    name='stlinfo',
    version='0.0.1',
    install_requires=[
        'numpy-stl'
    ],
    packages=find_packages(),
    scripts=['bin/stlinfo']
)
