from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dash-fda',
    version='0.1.0',
    description='Python starting project',
    long_description=readme,
    author='Name Surname',
    author_email='your-email@gmail.com',
    url='https://github.com/jackdbd/dash-fda',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
