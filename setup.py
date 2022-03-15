from setuptools import setup

setup(
    name='dhPLUS xmlRDFConverter',
    version='1.0',    
    description='xmlRDFConverter for dhPLUS data model',
    author='Peter Hinkelmanns',
    author_email='peter.hinkelmanns@sbg.ac.at',
    license="MIT",
    packages=['converter','xmlClasses'],
    install_requires=[
        'wheel',
        'autopep8',
        'isodate',
        'lxml',
        'pycodestyle',
        'pyparsing',
        'rdflib',
        'six',
        'toml',
        'tqdm'
        ],
)
