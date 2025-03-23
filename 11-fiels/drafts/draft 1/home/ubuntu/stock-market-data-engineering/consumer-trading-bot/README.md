# Consumer Trading Bot

This service implements automated trading strategies based on real-time stock market data from Kafka.

## Features

- Multiple trading strategies:
  - Moving Average Crossover
  - RSI (Relative Strength Index)
  - Bollinger Bands
- Risk management rules
- Position tracking
- Trading signal generation
- Historical data analysis

## Configuration

Edit `config.py` to modify:
- Kafka broker address and topic names
- PostgreSQL connection details
- Trading parameters (watchlist, position sizes)
- Strategy weights and thresholds
- Risk management settings

## Components

- **bot.py**: Main trading bot implementation
- **config.py**: Configuration parameters

## Requirements

- Python 3.8+
- Kafka broker accessible at the configured address
- PostgreSQL database for historical data and signal storage
- Dependencies listed in requirements.txt

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the trading bot:
```
python bot.py
```

## Docker

Build the Docker image:
```
docker build -t stock-trading-bot .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-trading-bot
```

## Trading Strategies

### Moving Average Crossover
Generates buy signals when the short-term moving average (7-day) crosses above the long-term moving average (20-day), and sell signals when it crosses below.

### RSI Strategy
Generates buy signals when RSI falls below 30 (oversold condition) and sell signals when RSI rises above 70 (overbought condition).

### Bollinger Bands
Generates buy signals when price touches the lower Bollinger Band and sell signals when price touches the upper Bollinger Band.

## Risk Management

The bot implements several risk management features:
- Maximum position size limits
- Maximum number of concurrent positions
- Stop loss and take profit levels
- Strategy weighting system to avoid false signals
