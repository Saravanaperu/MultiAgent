class VWAPStrategy:
    def __init__(self):
        self.name = "VWAP Reversal"

    def on_tick(self, tick):
        """
        Process incoming tick data and return order signal if conditions met.
        """
        # Logic: Price < VWAP - 0.3%, RSI < 30, Volume spike
        return None
