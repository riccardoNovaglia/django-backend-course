from app.calc import add, subtract
from django.test import TestCase


class CalcTest(TestCase):

    def test_add_number(self):
        self.assertEquals(add(3, 8), 11)

    def test_subtract(self):
        self.assertEquals(subtract(3, 2), 3)
