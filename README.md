# Dash FDA
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/jackdbd/dash-fda.svg?branch=master)](https://travis-ci.org/jackdbd/dash-fda) [![Updates](https://pyup.io/repos/github/jackdbd/dash-fda/shield.svg)](https://pyup.io/repos/github/jackdbd/dash-fda/) [![Python 3](https://pyup.io/repos/github/jackdbd/dash-fda/python-3-shield.svg)](https://pyup.io/repos/github/jackdbd/dash-fda/) [![Coverage](https://codecov.io/github/jackdbd/dash-fda/coverage.svg?branch=master)](https://codecov.io/github/jackdbd/dash-fda?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A Dash app to visualize data from the openFDA elasticsearch API.

![A GIF file showing a short demo on how to use the Dash FDA dashboard](https://github.com/jackdbd/dash-fda/blob/master/demo.gif "How to use the Dash FDA dashboard")

[App on Heroku](https://mighty-garden-67470.herokuapp.com/)

Built with:

- [Plotly Dash](https://plot.ly/products/dash/)
- [openFDA /device endpoint](https://open.fda.gov/device/)

Data from [openFDA](https://open.fda.gov/).


## Usage
Run all tests with:

```
python -m pytest -v
```

Install the app with:

```
python setup.py install
```

Run the app with:

```
cd dash-fda
python app.py
```

## Disclaimer
This app is just an independent project, and it has not been evaluated by the Food and Drug Administration.
This app is not intended to diagnose, treat, cure, or prevent any disease.
Do not rely on this app to make any decision regarding medical care.
