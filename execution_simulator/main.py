import redis
import json
import time
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

def execute_order(message):
    try:
        order = json.loads(message['data'])
        logger.info(f"Executing order: {order}")

        # Simulate slippage and fill
        slippage = random.uniform(0.0, 0.5)
        filled_price = order.get('price', 100) + slippage

        fill_report = {
            "order_id": order.get('id', 'unknown'),
            "symbol": order.get('symbol', 'NIFTY'),
            "filled_quantity": order.get('quantity', 1),
            "filled_price": filled_price,
            "timestamp": time.time(),
            "status": "FILLED"
        }

        logger.info(f"Order filled: {fill_report}")

        # Publish fill report
        redis_client.publish('orders:filled', json.dumps(fill_report))

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except KeyError as e:
        logger.error(f"Missing expected key: {e}")
    except TypeError as e:
        logger.error(f"Type error in order processing: {e}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error executing order: {e}")

def main():
    logger.info("Starting Execution Simulator...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe(**{'orders:validated': execute_order})

    thread = pubsub.run_in_thread(sleep_time=0.001)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Execution Simulator...")
        thread.stop()

if __name__ == "__main__":
    main()
