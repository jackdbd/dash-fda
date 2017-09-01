import unittest
import dash_html_components as html
from ddt import ddt, data
from dash_fda.app import app, _update_time_range_label, _update_graph


@ddt
class TestExample(unittest.TestCase):

    def test_layout_is_a_div_element(self):
        self.assertIsInstance(app.layout, html.Div)

    def test_debug_is_disabled(self):
        self.assertFalse(app.server.debug)

    def test_response_status_code_is_200(self):
        response = _update_time_range_label([-2000, 2010])
        self.assertEqual(response.status_code, 200)

    @data('COVIDIEN', 'GE+Healthcare', 'MEDTRONIC+MINIMED')
    def test_manufacturer_appears_in_reponse(self, manufacturer):
        response = _update_graph(manufacturer, [2000, 2010])
        self.assertIn(manufacturer, str(response.data))

if __name__ == '__main__':
    unittest.main()
