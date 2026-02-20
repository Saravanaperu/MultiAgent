import redis
import json
import time
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

class RiskManager:
    def __init__(self, refresh_interval=10):
        # Static Limits
        self.max_daily_loss = 5000.0
        self.max_per_trade_loss = 1000.0

        self.current_daily_loss = 0.0
        self._risk_multiplier = 1.0
        self._multiplier_lock = threading.Lock()
        self.refresh_interval = refresh_interval

        # Start background thread to refresh multiplier
        self._stop_event = threading.Event()
        self._multiplier_thread = threading.Thread(target=self._refresh_multiplier, daemon=True)
        self._multiplier_thread.start()

    @property
    def risk_multiplier(self):
        """Thread-safe access to risk multiplier."""
        with self._multiplier_lock:
            return self._risk_multiplier

    @risk_multiplier.setter
    def risk_multiplier(self, value):
        """Thread-safe update of risk multiplier."""
        with self._multiplier_lock:
            self._risk_multiplier = value

    def stop(self):
        """Stops the background refresh thread."""
        self._stop_event.set()
        self._multiplier_thread.join(timeout=1.0)

    def _refresh_multiplier(self):
        """Background task to refresh the AI multiplier from Redis."""
        while not self._stop_event.is_set():
            try:
                val = redis_client.get('ai:risk_multiplier')
                if val is not None:
                    self.risk_multiplier = float(val)
                    logger.debug(f"Refreshed AI Risk Multiplier: {self.risk_multiplier}")
            except Exception as e:
                logger.error(f"Error refreshing AI Risk Multiplier: {e}")

            # Efficiently wait for the next refresh or for a stop event
            self._stop_event.wait(timeout=self.refresh_interval)

    def check_order(self, order):
        """
        Validates order against risk rules.
        """
        logger.info(f"Checking order: {order}")

        # Check Daily Loss
        if self.current_daily_loss >= self.max_daily_loss:
            logger.warning("Daily loss limit reached. Order rejected.")
            return False

        # Dynamic Check: Use Cached AI Multiplier
        current_multiplier = self.risk_multiplier
        logger.info(f"Applying AI Risk Multiplier: {current_multiplier}")

        # Adjust order size based on multiplier (simulated)
        # order['quantity'] = int(order['quantity'] * current_multiplier)

        return True

rm = RiskManager()

def process_order_request(message):
    try:
        order_data = json.loads(message['data'])
        if rm.check_order(order_data):
            logger.info("Order approved. Forwarding to execution...")
            redis_client.publish('orders:validated', json.dumps(order_data))
        else:
            logger.info("Order rejected by Risk Manager.")
    except Exception as e:
        logger.error(f"Error validating order: {e}")

def main():
    logger.info("Starting Risk Management Engine...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe(**{'orders:incoming': process_order_request})

    thread = pubsub.run_in_thread(sleep_time=0.001)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Risk Management Engine...")
        rm.stop()
        thread.stop()

if __name__ == "__main__":
    main()
