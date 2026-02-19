import redis
import json
import time
import logging
from strategies.momentum import MomentumStrategy
from strategies.vwap import VWAPStrategy
from strategies.gamma import GammaStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

strategies = [
    MomentumStrategy(),
    VWAPStrategy(),
    GammaStrategy()
]

def process_tick(message):
    try:
        tick_data = json.loads(message['data'])
        for strategy in strategies:
            signal = strategy.on_tick(tick_data)
            if signal:
                logger.info(f"Signal generated: {signal}")
                # Publish order signal
                redis_client.publish('orders:incoming', json.dumps(signal))
    except Exception as e:
        logger.error(f"Error processing tick: {e}")

def main():
    logger.info("Starting Strategy Engine...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe(**{'market:tick': process_tick})

    logger.info("Subscribed to market:tick")

    # Run the event loop
    thread = pubsub.run_in_thread(sleep_time=0.001)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Strategy Engine...")
        thread.stop()

if __name__ == "__main__":
    main()
