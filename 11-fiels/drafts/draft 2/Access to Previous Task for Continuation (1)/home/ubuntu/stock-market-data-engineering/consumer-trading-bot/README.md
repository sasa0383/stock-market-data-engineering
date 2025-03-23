# Consumer Trading Bot

## Overview
The Consumer Trading Bot service analyzes stock market data in real-time and generates trading signals based on various technical analysis strategies. It consumes stock price data from Kafka topics, applies trading algorithms, and produces trading signals.

## Features
- Real-time analysis of stock price data
- Multiple trading strategies:
  - Moving Average Crossover
  - Relative Strength Index (RSI)
  - Bollinger Bands
- Risk management settings
- Backtesting capabilities
- Configurable for multiple symbols

## Components
1. **Trading Bot**: Main logic for analyzing data and generating signals
2. **Trading Strategies**: Algorithms for identifying trading opportunities
3. **Risk Management**: Rules for managing position sizes and risk

## Requirements
- Python 3.9+
- Kafka Python client
- Pandas and NumPy for data analysis
- Requests for API calls
- Matplotlib and scikit-learn for advanced analysis

## Configuration
Edit the `config.py` file to customize:
- Kafka broker address and topics
- API key and base URL
- Symbols to track
- Trading strategy parameters
- Risk management settings
- Backtesting parameters

## Usage
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the trading bot:
   ```
   python bot.py
   ```

## Docker Usage
Build the Docker image:
```
docker build -t stock-trading-bot .
```

Run the container:
```
docker run --network=stock-market-data-engineering_default stock-trading-bot
```

## Data Flow
1. Bot consumes stock price data from Kafka topic
2. Data is processed and analyzed using trading strategies
3. Trading signals are generated based on analysis
4. Signals are logged and can be sent to a Kafka topic
5. (Optional) Trades can be executed via brokerage API

## Trading Strategies
### Moving Average Crossover
- Buy signal: Short MA crosses above Long MA
- Sell signal: Short MA crosses below Long MA

### Relative Strength Index (RSI)
- Buy signal: RSI below oversold threshold (default: 30)
- Sell signal: RSI above overbought threshold (default: 70)

### Bollinger Bands
- Buy signal: Price crosses below lower band
- Sell signal: Price crosses above upper band

## Risk Management
The bot includes configurable risk management settings:
- Maximum position size as percentage of portfolio
- Stop loss percentage
- Take profit percentage
