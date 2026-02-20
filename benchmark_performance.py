import time
import sys
import unittest.mock as mock
from types import ModuleType

# Mock redis module before importing main
mock_redis = ModuleType('redis')
sys.modules['redis'] = mock_redis
mock_redis.Redis = mock.Mock()

# Now import RiskManager
from risk_management.main import RiskManager
import risk_management.main

# Simulated Redis client with latency
class LatencyRedis:
    def __init__(self, latency=0.002):
        self.latency = latency
        self.data = {'ai:risk_multiplier': b'1.2'}

    def get(self, key):
        time.sleep(self.latency)
        return self.data.get(key)

def run_benchmark():
    real_redis = LatencyRedis(latency=0.002) # 2ms latency
    risk_management.main.redis_client = real_redis

    rm = RiskManager()
    order = {'symbol': 'NIFTY24DEC25000CE', 'quantity': 50, 'price': 100}

    # 1. Sync Logic (Simulated original behavior)
    print("Starting sync benchmark (1000 calls)...")
    start = time.time()
    for _ in range(1000):
        # Simulated sync logic: network call for every check
        _ = float(real_redis.get('ai:risk_multiplier') or 1.0)
        _ = rm.current_daily_loss >= rm.max_daily_loss
    end = time.time()
    sync_duration = end - start

    # 2. Cached Logic (Current optimized behavior)
    print("Starting cached benchmark (1000 calls)...")
    start = time.time()
    for _ in range(1000):
        rm.check_order(order)
    end = time.time()
    cached_duration = end - start

    print("-" * 40)
    print(f"Sync duration:   {sync_duration:.4f}s ({1000/sync_duration:.2f} orders/sec)")
    print(f"Cached duration: {cached_duration:.4f}s ({1000/cached_duration:.2f} orders/sec)")

    improvement = (sync_duration - cached_duration) / sync_duration * 100
    print(f"Improvement:      {improvement:.2f}%")
    print("-" * 40)

    rm.stop()

if __name__ == "__main__":
    run_benchmark()
