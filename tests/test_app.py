import requests
import unittest
import dash_html_components as html
from ddt import ddt, data
from flask import json
from .context import app, update_table, URL_PREFIX


@ddt
class TestExample(unittest.TestCase):
    def test_layout_is_a_function_that_returns_a_div_element(self):
        self.assertIsInstance(app.layout(), html.Div)

    def test_debug_is_disabled(self):
        self.assertFalse(app.server.debug)

    def test_not_found_404(self):
        url = f"{URL_PREFIX}&search=device.generic_name:XYZ&limit=1"
        res = requests.get(url)
        self.assertEqual(res.status_code, 404)

    def test_bad_request_400(self):
        """In the openFDA API limit cannot exceed 1000 results."""
        url = f"{URL_PREFIX}&limit=1001"
        res = requests.get(url)
        self.assertEqual(res.status_code, 400)

    @unittest.skip("TODO: how to unit-test Dash callbacks?")
    def test_response_status_code_is_200(self):
        response = update_table(1, [1991, 2017], "COVIDIEN", "ligasure")
        self.assertEqual(response.status_code, 200)

    @unittest.skip("TODO: how to unit-test Dash callbacks?")
    @data("COVIDIEN", "GE+Healthcare", "MEDTRONIC+MINIMED")
    def test_no_results_in_table_when_input_is_missing(self, manufacturer):
        response = update_table(1, [1991, 2017], manufacturer, "")
        d = json.loads(response.data)
        self.assertListEqual(d["response"]["props"]["rows"], [])


if __name__ == "__main__":
    unittest.main()
