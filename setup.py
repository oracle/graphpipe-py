import setuptools

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

requirements = None
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='graphpipe',
    version='1.0.4',
    description='Graphpipe client and helpers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='OCI ML Team',
    install_requires=requirements,
    author_email='vish.ishaya@oracle.com',
    url='https://oracle.github.io/graphpipe',
    classifier=[
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: Universal Permissive License (UPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests']),
)
