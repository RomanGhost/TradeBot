import numpy as np
import logging

#logging.basicConfig(level=logging.INFO, filename='app_metrics.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

class Data:
    def __init__(self, period):
        self.period = period
        self.values = list()

    def addValue(self, value):
        self.values.append(value)
        lenght = len(self.values)
        if lenght >= self.period:
            self.values = self.values[-self.period:]
            return 1

    def getValue(self):
        return self.values.copy()


class Metrics:
    def __init__(self, data: Data, period):
        self.period = period
        self.data = data

    def calc(self):
        if len(self.data.values) < self.period:
            return
        return 1


class RSI(Metrics):
    def __init__(self, data: Data, period=14):
        super().__init__(data, period)

    def calc(self):

        price_changes = [self.data.values[i] - self.data.values[i - 1] for i in range(1, len(self.data.values))]
        gains = [change if change > 0 else 0 for change in price_changes]
        losses = [-change if change < 0 else 0 for change in price_changes]

        try:
            avg_gain = sum(gains[:self.period]) / self.period
        except ZeroDivisionError:
            logging.error('Error RSI; ZeroDivision: avg_gain')
            avg_gain = 1

        try:
            avg_loss = sum(losses[:self.period]) / self.period
        except ZeroDivisionError:
            logging.error('Error RSI; ZeroDivision: avg_loss')
            avg_loss = 1

        rsi_values = []

        for i in range(self.period, len(price_changes)):
            try:
                avg_gain = ((avg_gain * (self.period - 1)) + gains[i - 1]) / self.period
            except ZeroDivisionError:
                logging.error('Error RSI; ZeroDivision: avg_gain in cycle')
                avg_gain = 1

            try:
                avg_loss = ((avg_loss * (self.period - 1)) + losses[i - 1]) / self.period
            except ZeroDivisionError:
                logging.error('Error RSI; ZeroDivision: avg_loss in cycle')
                avg_loss = 1

            try:
                relative_strength = avg_gain / avg_loss
            except ZeroDivisionError:
                logging.error('Error RSI; ZeroDivision: relative_strength')
                relative_strength = 0
            rsi = 100 - (100 / (1 + relative_strength))

            rsi_values.append(rsi)

        # возвращаем сразу 2 значения, чтобы не инициализировать в главной программе
        return rsi_values[-2:]


class SO(Metrics):
    def __init__(self, data: Data, k_period=14, d_period=3):
        super().__init__(data, k_period)
        self.d_period = d_period
    def calc(self, ):
        highest_highs = []
        lowest_lows = []

        for i in range(len(self.data.values) - self.period + 1):
            highest_high = max(self.data.values[i:i + self.period])
            lowest_low = min(self.data.values[i:i + self.period])
            highest_highs.append(highest_high)
            lowest_lows.append(lowest_low)

        k_values = list()
        for i in range(len(highest_highs)):
            try:
                k_value = (self.data.values[i + self.period - 1] - lowest_lows[i]) / (highest_highs[i] - lowest_lows[i]) * 100
            except ZeroDivisionError:
                logging.error('Error SO; ZeroDivision: k_value')
                k_value = 0

            k_values.append(k_value)

        d_values = sum(k_values[-self.d_period:]) / self.d_period

        return k_values[-1], d_values


class MACD(Metrics):
    def __init__(self, data: Data, short_period=16, long_period=26):
        if short_period > long_period:
            raise ValueError("fast must to less that slow")

        super().__init__(data, short_period)
        self.long_period = long_period

    def calc(self):
        short_ema = sum(self.data.values[-self.period:]) / self.period
        long_ema = sum(self.data.values[-self.long_period:]) / self.long_period
        if long_ema == 0:
            return 0
        return (short_ema / long_ema - 1) * 100


class SAR(Metrics):
    def __init__(self, data: Data,
                 acceleration_factor_initial=0.02,
                 acceleration_factor_increment=0.02,
                 acceleration_factor_maximum=0.2):
        super().__init__(data, 4)
        self.acceleration_factor_initial = acceleration_factor_initial
        self.acceleration_factor_increment = acceleration_factor_increment
        self.acceleration_factor_maximum = acceleration_factor_maximum

    def calculate_parabolic_sar(self):
        sar_values = None
        extreme_point = self.data.values[0]
        acceleration_factor = self.acceleration_factor_initial
        sar = self.data.values[0]  # Initial SAR value

        for i in range(2, len(self.data.values)):
            if self.data.values[i - 1] > sar:
                sar = sar + acceleration_factor * (extreme_point - sar)
                sar = max(sar, self.data.values[i - 2], self.data.values[i - 1])
                extreme_point = self.data.values[i - 1]
                if sar > self.data.values[i]:
                    sar = extreme_point
                    acceleration_factor = self.acceleration_factor_initial
            else:
                sar = sar + acceleration_factor * (extreme_point - sar)
                sar = min(sar, self.data.values[i - 2], self.data.values[i - 1])
                extreme_point = self.data.values[i - 1]
                if sar < self.data.values[i]:
                    sar = extreme_point
                    acceleration_factor = self.acceleration_factor_initial

            acceleration_factor = min(acceleration_factor + self.acceleration_factor_increment, self.acceleration_factor_maximum)
            sar_values = sar

        return sar_values
