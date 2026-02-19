import time
import random

class AngelOneClient:
    def __init__(self, api_key, client_id, password):
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.connected = False

    def login(self):
        """Authenticates with Angel One API."""
        print(f"Logging in user {self.client_id}...")
        # Simulate login delay
        time.sleep(1)
        print("Login successful.")
        self.connected = True

    def connect_websocket(self, on_tick):
        """Connects to WebSocket and subscribes to ticks."""
        print("Connecting to WebSocket...")
        # Simulate websocket connection
        self._simulate_ticks(on_tick)

    def _simulate_ticks(self, callback):
        """Simulate tick data for skeleton purposes."""
        import threading

        def run():
            while self.connected:
                # Generate random tick
                tick = {
                    "symbol": "NIFTY23NOV19800CE",
                    "ltp": random.uniform(100, 150),
                    "volume": random.randint(1000, 5000),
                    "timestamp": time.time()
                }
                callback(tick)
                time.sleep(1) # 1 tick per second

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
