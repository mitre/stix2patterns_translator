from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stix-pattern-translator',

    version='0.1.0',

    description='A translator to convert STIX2 patterns into other search platforms (e.g., ElasticSearch) and data models (e.g., CIM)',
    long_description=long_description,

    url='https://github.com/mitre/stix2patterns_translator',

    author='The MITRE Corporation',
    
    author_email = 'hfoster@mitre.org',

    license='Apache License 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Security',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='stix cybersecurity analytics',

    packages=find_packages(exclude=['tests']),

    install_requires=['antlr4-python3-runtime', 'python-dateutil'],

    extras_require={
        'dev': ['pytest', 'tox', 'flask', 'requests'],
        'web': ['flask'],
    },

    package_data={},

    data_files=[],

    entry_points={
        'console_scripts': [
            'translate-stix-pattern=stix2patterns_translator.translator:main',
            'pattern-translator-server=stix2patterns_translator.web_api:main',
        ],
    },
)
