from setuptools import setup, find_packages

setup(
    name='api',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-CORS',
        'click',
        'elasticsearch-dsl',
        'elasticsearch',
        'luminoth',
    ],
)
