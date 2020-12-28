from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils
from jesse.helpers import get_candle_source
import talib


class ExampleStrategy(Strategy):
    def should_long(self) -> bool:
        if self.rsi_trigger > self.dc_upper:
            return True
        return False

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        return False

    def go_long(self):
        stop = self.price * (1 - 5 / 100)
        qty = utils.risk_to_qty(self.capital, 100, stop, self.fee_rate)
        self.buy = qty, self.price
        self.stop_loss = qty, stop

    def update_position(self):
        if self.rsi_trigger < self.dc_lower:
            self.liquidate()

    def go_short(self):
        pass

    def hyperparameters(self):
        return [
            {'name': 'rsi_len', 'type': int, 'min': 2, 'max': 30, 'default': 14},
            {'name': 'smoother_len', 'type': int, 'min': 2, 'max': 10, 'default': 5},
            {'name': 'dc_upper_len', 'type': int, 'min': 1, 'max': 300, 'default': 45},
            {'name': 'dc_lower_len', 'type': int, 'min': 1, 'max': 300, 'default': 165},
        ]

    @property
    def rsi_trigger(self):
        return ta.rsi(self.candles, self.hp['rsi_len'])

    @property
    def rsi(self):
        source = get_candle_source(self.candles, source_type="close")
        return talib.RSI(source, self.hp['rsi_len'])

    @property
    def dc_upper(self):
        return talib.MAX(self.rsi, timeperiod=self.hp['dc_upper_len'])[-1]

    @property
    def dc_lower(self):
        return talib.MAX(self.rsi, timeperiod=self.hp['dc_lower_len'])[-1]
