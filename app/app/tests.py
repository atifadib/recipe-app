"""
Sample tests
"""
from django.test import SimpleTestCase

from app import calc


class TestCalc(SimpleTestCase):
    """ Testing calc methods"""
    def test_add_numbers(self):
        res = calc.add(5, 6)
        self.assertEqual(res, 11)
