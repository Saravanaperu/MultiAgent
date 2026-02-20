import redis
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

class RiskManager:
    def __init__(self):
        # Static Limits
        self.max_daily_loss = 5000.0
        self.max_per_trade_loss = 1000.0

        self.current_daily_loss = 0.0

    def check_order(self, order):
        """
        Validates order against risk rules.
        """
        logger.info(f"Checking order: {order}")

        # Check Daily Loss
        if self.current_daily_loss >= self.max_daily_loss:
            logger.warning("Daily loss limit reached. Order rejected.")
            return False

        # Dynamic Check: Check AI Multiplier
        risk_multiplier = float(redis_client.get('ai:risk_multiplier') or 1.0)
        logger.info(f"Applying AI Risk Multiplier: {risk_multiplier}")

        # Adjust order size based on multiplier
        order['quantity'] = int(order['quantity'] * risk_multiplier)

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
        thread.stop()

if __name__ == "__main__":
    main()
