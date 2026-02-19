class MomentumStrategy:
    def __init__(self):
        self.name = "Momentum Breakout"

    def on_tick(self, tick):
        """
        Process incoming tick data and return order signal if conditions met.
        """
        # Logic: 9-EMA crosses 21-EMA, Price > VWAP + 0.5%, etc.
        # This is a skeleton, so returning None or a dummy signal.
        return None
