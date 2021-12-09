from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTest(TestCase):

    def test_wait_for_db_to_be_ready(self):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertTrue(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_tries_5_times_and_stops(self, _ts):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertTrue(gi.call_count, 6)
