# Dash FDA

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/jackdbd/dash-fda.svg?branch=master)](https://travis-ci.org/jackdbd/dash-fda) [![Coverage](https://codecov.io/github/jackdbd/dash-fda/coverage.svg?branch=master)](https://codecov.io/github/jackdbd/dash-fda?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A Dash app to visualize data from the openFDA elasticsearch API.

![A GIF file showing a short demo on how to use the Dash FDA dashboard](https://github.com/jackdbd/dash-fda/blob/master/demo.gif "How to use the Dash FDA dashboard")

[App on CapRover](https://cutt.ly/dash-fda).

Built with:

- [Plotly Dash](https://plotly.com/dash/)
- [openFDA /device endpoint](https://open.fda.gov/device/)

Data from [openFDA](https://open.fda.gov/).

## API keys

This project requires to get some API keys from external services.

- `PLOTLY_USERNAME`, `PLOTLY_API_KEY`: get them at [chart-studio.plotly.com](https://chart-studio.plotly.com/).
- `OPEN_FDA_API_KEY`: get it at [openFDA](https://open.fda.gov/apis/authentication/)

## Installation

This project uses [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to manage the Python virtual environment, and [poetry](https://poetry.eustace.io/) to manage the project dependencies.

If you don't already have it, install python `3.8.5`.

```shell
pyenv install 3.8.5
```

Create a virtual environment and activate it.

```shell
pyenv virtualenv 3.8.5 dash_fda
pyenv activate dash_fda
```

Remember to activate the virtual environment every time you work on this project.

Install all the dependencies from the `poetry.lock` file.

```shell
poetry install
```

## Tasks

This project uses the task runner [Poe the Poet](https://github.com/nat-n/poethepoet) to run poetry scripts.

## Non-dockerized app

Run the app locally using a development server (Dash uses a Flask development server):

```shell
poetry run poe dev

# or, in alternative
python app.py
```

Run the app locally using a production server (gunicorn):

```shell
poetry run poe prod
```

Run all tests with pytest:

```shell
poetry run poe test
```

Format all code with black:

```shell
poetry run poe format
```

## Dockerized app

Build the Docker image and give it a name and a version tag:

```shell
docker build -t dash-fda:v0.1.0 .
```

Run the Docker container:

```shell
docker run --env-file ./dash_fda/.env -p 5001:5000 dash-fda:v0.1.0
```

Deploy the dockerized app on CapRover (running on my DigitalOcean Droplet):

```shell
./deploy.sh
```

## Troubleshooting

If you are on Ubuntu you might get `ModuleNotFoundError: No module named '_bz2'` and/or `UserWarning: Could not import the lzma module. Your installed Python is incomplete. Attempting to use lzma compression will result in a RuntimeError.` These errors are caused by pandas when it tries to import these [compression libraries](https://github.com/pandas-dev/pandas/issues/27575). If you get these errors you need to install the libbz2-dev package and the liblzma-dev package, then re-compile your python interpreter.

Here is how you can do it:

```shell
# deactivate and remove the virtual environment
pyenv deactivate
pyenv virtualenv-delete dash_fda

# remove the "broken" python interpreter
pyenv uninstall 3.8.5

# install the compression libreries
sudo apt-get install libbz2-dev liblzma-dev

# download and compile the python interpreter
pyenv install 3.8.5

# re-create the virtual environment and activate it
pyenv virtualenv 3.8.5 dash_fda
pyenv activate dash_fda

# re-install all the dependencies
poetry install
```

## Disclaimer

This app is just an independent project, and it has not been evaluated by the Food and Drug Administration.
This app is not intended to diagnose, treat, cure, or prevent any disease.
Do not rely on this app to make any decision regarding medical care.
