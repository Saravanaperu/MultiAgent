import os
import time
import redis
import json
import logging
from angel_one_client import AngelOneClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis Connection
redis_client = redis.Redis(host='redis', port=6379, db=0)

def publish_tick(tick_data):
    """Publishes tick data to Redis channel."""
    try:
        redis_client.publish('market:tick', json.dumps(tick_data))
        logger.debug(f"Published tick: {tick_data}")
    except Exception as e:
        logger.error(f"Error publishing tick: {e}")

def main():
    logger.info("Starting Market Data Engine...")

    # Initialize Angel One Client (Placeholder)
    api_key = os.getenv("ANGEL_API_KEY", "test_key")
    client_id = os.getenv("ANGEL_CLIENT_ID", "test_id")
    password = os.getenv("ANGEL_PASSWORD", "test_pass")

    client = AngelOneClient(api_key, client_id, password)

    # Connect and subscribe (Simulated for skeleton)
    try:
        client.login()
        client.connect_websocket(on_tick=publish_tick)

        while True:
            # Keep the main thread alive
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Stopping Market Data Engine...")
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
