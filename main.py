import time
from binance.client import Client
import spech
from bot import Bot
import metrics
import logging

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

max_period = 30

data = metrics.Data(max_period)
metric_so = metrics.SO(data, 15, 3)
metrics_rsi = metrics.RSI(data, 15)
metrics_macd = metrics.MACD(data, 12, 28)
metrics_sar = metrics.SAR(data, 0.02, 0.02, 0.2)

eth_bot = Bot(percent=[55, 60, 40, 35], barier_buy=95, barier_sell=50)

client = Client(spech.api_key, spech.security_key, testnet=True)

# Собираем данные за последний час, чтобы не ждать
agg_trades = list(client.aggregate_trade_iter(symbol='ETHUSDT', start_str='60 minutes ago UTC'))
trade_start = agg_trades[0]
for trade in agg_trades:
    if trade['T'] - trade_start['T'] >= 60_000:
        trade_start = trade
        data.addValue(float(trade['p']))
print(len(data.values))

def main(run=True):
    while run:
        ping = client.ping()
        logging.info(f'Start wait info from Binance, {ping}')
        time.sleep(61)
        agg_trades = list(client.aggregate_trade_iter(symbol='ETHUSDT', start_str='2 minutes ago UTC'))

        try:
            price = float(agg_trades[-1]['p'])
        except IndexError:
            continue

        print(f'Price:{price}')
        res = data.addValue(price)
        if res != 1:
            continue

        so = metric_so.calc()
        rsi = metrics_rsi.calc()
        macd = metrics_macd.calc()
        sar = metrics_sar.calc()

        predict_res = eth_bot.predict(rsi, so, macd, price, sar)
        print(eth_bot.balance)
        logging.info(f'We {predict_res}: {eth_bot.balance}; price of ETHUSTD: {price}')

try:
    main()
except KeyboardInterrupt:
    logging.error('KeyboardInterrupt; Code is stop. Look why!')
    print(eth_bot.balance)
except Exception as e:
    logging.error(f'Something error; {e}, {data.values}')
