class GammaStrategy:
    def __init__(self):
        self.name = "Gamma Scalping Window"

    def on_tick(self, tick):
        """
        Process incoming tick data and return order signal if conditions met.
        """
        # Logic: High-volatility window, IV > 90th percentile
        return None
