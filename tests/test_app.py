import unittest
import dash_html_components as html
from ddt import ddt, data
from dash_fda.app import app, _update_graph, _update_table


@ddt
class TestExample(unittest.TestCase):

    def test_layout_is_a_function_that_returns_a_div_element(self):
        self.assertIsInstance(app.layout(), html.Div)

    def test_debug_is_disabled(self):
        self.assertFalse(app.server.debug)

    def test_response_status_code_is_200(self):
        response = _update_table(1, 'COVIDIEN', '1991-01-01', '2017-01-11')
        self.assertEqual(response.status_code, 200)

    @data('COVIDIEN', 'GE+Healthcare', 'MEDTRONIC+MINIMED')
    def test_manufacturer_appears_in_reponse(self, manufacturer):
        response = _update_graph(1, manufacturer, '1991-01-01', '2017-01-11')
        self.assertIn(manufacturer, str(response.data))

if __name__ == '__main__':
    unittest.main()
