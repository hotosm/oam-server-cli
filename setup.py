from setuptools import setup, find_packages

setup(
    name='python-oam',
    version='0.1.0',
    author='Azavea',
    author_email='info@azavea.com',
    maintainer='Rob Emanuele',
    maintainer_email='remanuele@azavea.com',
    packages=find_packages(),
    url=['http://github.com/hotosm-oam/oam-server-cli'],
    scripts=['bin/oam'],
    license='LICENSE.txt',
    description='Command line client for interacting with OpenAerialMap',
    long_description=open('README.md').read(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: GIS',
        'Programming Language :: Python :: 2.7'
    ],
)
