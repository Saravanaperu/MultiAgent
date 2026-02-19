import redis
import json
import time
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

# In-memory trade log (Replace with DB for production)
trade_log = []

def log_trade(message):
    try:
        trade_data = json.loads(message['data'])
        logger.info(f"Logging trade: {trade_data}")

        trade_log.append(trade_data)

        # Calculate analytics (simplified)
        df = pd.DataFrame(trade_log)
        if not df.empty:
            analytics = {
                "total_trades": len(df),
                "last_trade_price": trade_data.get('filled_price')
            }
            logger.info(f"Analytics updated: {analytics}")

    except Exception as e:
        logger.error(f"Error logging trade: {e}")

def main():
    logger.info("Starting Trade Journal & Analytics...")
    pubsub = redis_client.pubsub()
    pubsub.subscribe(**{'orders:filled': log_trade})

    thread = pubsub.run_in_thread(sleep_time=0.001)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Trade Journal...")
        thread.stop()

if __name__ == "__main__":
    main()
