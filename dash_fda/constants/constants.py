import os
import chart_studio
from dotenv import load_dotenv
from dash_fda.exceptions import ImproperlyConfigured


DEBUG = False


if "DYNO" in os.environ:
    # the app is on Heroku
    DEBUG = False
else:
    DEBUG = True
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    # print("=== dotenv_path ===", dotenv_path)
    load_dotenv(dotenv_path)


if os.environ.get("SECRET_KEY") is None:
    raise ImproperlyConfigured("SECRET_KEY (for Flask) not set in .env")
SECRET_KEY = os.environ.get("SECRET_KEY")

if os.environ.get("PLOTLY_USERNAME") is None:
    raise ImproperlyConfigured("PLOTLY_USERNAME not set in .env")
if os.environ.get("PLOTLY_API_KEY") is None:
    raise ImproperlyConfigured("PLOTLY_API_KEY not set in .env")
chart_studio.tools.set_credentials_file(
    os.environ["PLOTLY_USERNAME"], os.environ["PLOTLY_API_KEY"]
)


MANUFACTURERS = [
    {"label": "Covidien", "value": "COVIDIEN"},
    {"label": "Esaote", "value": "ESAOTE"},
    {"label": "Dräger", "value": "DRAEGER"},
    {
        "label": "GE Healthcare",
        "value": "GE+Healthcare",
    },
    {
        "label": "Medtronic",
        "value": "MEDTRONIC+MINIMED",
    },
    {"label": "Zimmer", "value": "ZIMMER+INC."},
    {
        "label": "Baxter",
        "value": "BAXTER+HEALTHCARE+PTE.+LTD.",
    },
    {
        "label": "Smiths Medical",
        "value": "SMITHS+MEDICAL+MD+INC.",
    },
]

APP_NAME = "Dash FDA"

openFDA = "https://api.fda.gov/"

API_ENDPOINT = "device/event.json?"

API_KEY = os.environ.get("OPEN_FDA_API_KEY")

if API_KEY is None:
    raise ImproperlyConfigured("OPEN_FDA_API_KEY not set in .env")

URL_PREFIX = f"{openFDA}{API_ENDPOINT}api_key={API_KEY}"

INITIAL_URL = f"{URL_PREFIX}&count=date_of_event"
