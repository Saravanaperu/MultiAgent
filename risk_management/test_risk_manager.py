import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock redis before importing the module
mock_redis_module = MagicMock()
sys.modules['redis'] = mock_redis_module

# Add the project root to sys.path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from risk_management.main import RiskManager

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.rm = RiskManager()

    @patch('risk_management.main.redis_client')
    def test_check_order_multiplies_quantity(self, mock_redis):
        # Setup mock redis return value
        mock_redis.get.return_value = b'1.5'

        order = {'quantity': 100, 'symbol': 'NIFTY26FEB20000CE'}
        result = self.rm.check_order(order)

        self.assertTrue(result)
        self.assertEqual(order['quantity'], 150)
        mock_redis.get.assert_called_with('ai:risk_multiplier')

    @patch('risk_management.main.redis_client')
    def test_check_order_default_multiplier(self, mock_redis):
        # Setup mock redis to return None (defaulting to 1.0)
        mock_redis.get.return_value = None

        order = {'quantity': 100, 'symbol': 'NIFTY26FEB20000CE'}
        result = self.rm.check_order(order)

        self.assertTrue(result)
        self.assertEqual(order['quantity'], 100)

    @patch('risk_management.main.redis_client')
    def test_check_order_low_multiplier(self, mock_redis):
        # Setup mock redis return value
        mock_redis.get.return_value = b'0.5'

        order = {'quantity': 100, 'symbol': 'NIFTY26FEB20000CE'}
        result = self.rm.check_order(order)

        self.assertTrue(result)
        self.assertEqual(order['quantity'], 50)

if __name__ == '__main__':
    unittest.main()
