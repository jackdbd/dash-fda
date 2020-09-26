import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
import dash_fda
from dash_fda.constants import URL_PREFIX
from dash_fda.app import app, update_table
