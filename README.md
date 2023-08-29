# TradingBot
My hobby about finance

# О проекте
В данном проекте реализован бот для алгоритмической торговли. 
#### Для принятия решений бот использует инструменты:
- RSI
- Stochastic Oscillator
- MACD
- Parabolic SAR 

Влияние инструмента на покупку или продажи прописывается при создании обекта класса Bot.

# Сборка проекта
Клонировать проект

``` sh
git clone <path to repo>
cd TradeBot
```

После нужно создать python файл *spech.py* по образцу:
``` python
api_key = 'your api key from binance'
security_key = 'your secrity key from binance'
```

Теперь собрать весь проект в с помощью **Docker**
``` sh
docker build -t <container-name> .
docker run -d <container-name>
```
Заменить **<container-name>** на имя контейнера

После можно проверить, что контейнер запущен
``` sh
docker ps
```

# Заметки
Весь проект в контейнере находится в папке */app*
Во время работы проекта генерируется файл */app/app.log*
При изменеии параметров нужно следить, чтобы они были достежимы.
