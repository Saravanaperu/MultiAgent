import unittest
import sys
import time
import threading
import unittest.mock as mock
from types import ModuleType

# Mock redis module
if 'redis' not in sys.modules:
    mock_redis = ModuleType('redis')
    sys.modules['redis'] = mock_redis
    mock_redis.Redis = mock.Mock()

from risk_management.main import RiskManager
import risk_management.main

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.mock_redis = mock.Mock()
        risk_management.main.redis_client = self.mock_redis
        # Make sure mock_redis.get returns a valid value for the thread
        self.mock_redis.get.return_value = b'1.0'
        # Use a very short refresh interval for testing
        self.rm = RiskManager(refresh_interval=0.1)

    def tearDown(self):
        self.rm.stop()

    def test_daily_loss_limit(self):
        self.rm.current_daily_loss = 6000.0
        order = {'quantity': 10}
        self.assertFalse(self.rm.check_order(order))

    def test_risk_multiplier_thread_safety(self):
        # Test that we can read/write multiplier from multiple threads without crashing
        def worker():
            for _ in range(100):
                self.rm.risk_multiplier = 1.2
                _ = self.rm.risk_multiplier

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(self.rm.risk_multiplier, 1.2)

    def test_background_refresh_actually_runs(self):
        # Initial value is 1.0 (from setUp)
        # Change value in mock Redis
        self.mock_redis.get.return_value = b'1.5'

        # Wait for at least one refresh cycle (interval is 0.1s)
        time.sleep(0.3)

        # Check if the value was updated
        self.assertEqual(self.rm.risk_multiplier, 1.5)

    def test_background_refresh_error_handling(self):
        # Test that the thread survives an exception
        self.mock_redis.get.side_effect = [Exception("Redis error"), b'0.7']

        time.sleep(0.3)
        # After the first failure, the next successful refresh should work
        self.assertEqual(self.rm.risk_multiplier, 0.7)

if __name__ == '__main__':
    unittest.main()
