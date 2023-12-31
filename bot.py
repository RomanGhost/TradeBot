class Bot:
    def __init__(self, percent=[55, 60, 40, 35], barier_buy=95, barier_sell=50):
        self.percent = percent
        self.barier_buy = barier_buy
        self.barier_sell = barier_sell
        self.money = 0
        self.balance = 0

    def buy(self, price, count=1):
        self.money += count
        self.balance -= price

    def sell(self, price, count=1):
        if self.money <= 0:
            return

        self.money -= count
        self.balance += price

    def predict(self, rsi, so, macd, sar, price):
        """
        rsi: list, shape = 1, 2 (0-100)
        so: list, shape = 1, 2 (0-100)(0,1)
        macd: float, (-100, 100)
        sar: int, (-1, 1)
        """
        # покупка
        res = 0

        sar_bin = 0
        if sar > price:
            sar_bin = 1
        elif sar < price:
            sar_bin = -1

        # высчитываем как идет тренд 0 - пересекаются, >100 k>d(), <-100 k<d
        k, d = so
        try:
            k_d = k / d - 1 * 100
        except ZeroDivisionError:
            k_d = 0

        # если предыдущее значение меньше(идет вверх), значение сейчас меньше 30
        if rsi[0] < rsi[1] < 30:
            res += self.percent[0]

        # последнее значение меньше 20, относительно показателя d выше
        if k < 20 and k_d > 12:
            res += self.percent[1]

        # быстрое значение пересекает медленное идя вверх
        if macd < -0.06:
            res += self.percent[2]

        # если точка ниже цены
        if sar_bin == -1:
            res += self.percent[3]

        if res >= self.barier_buy:
            self.buy(price)
            return 2

        # продажа
        res = 0

        # если предыдущее значение больше(идет вниз), значение сейчас больше 70
        if rsi[0] > rsi[1] > 70:
            res += self.percent[0]

        # последнее значение больше 80, относительно показателя d ниже
        if k > 80 and k_d < -8:
            res += self.percent[1]

        # быстрое значение пересекает медленное идя вниз
        if macd > 0.021:
            res += self.percent[2]

        # если точка выше цены
        if sar_bin == 1:
            res += self.percent[3]

        if res >= self.barier_sell:
            self.sell(price)
            return 0

        return 1
