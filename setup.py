from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dash_fda',
    version='0.1.0',
    description='A Dash app displaying data from the openFDA elasticsearch API',
    long_description=readme,
    author='Giacomo Debiddda',
    author_email='jackdebidda@gmail.com',
    url='https://github.com/jackdbd/dash-fda',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
