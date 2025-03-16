#!/usr/bin/env python3
"""
Trading Bot for Stock Market Data Engineering Project
Performs trading logic and real-time analysis on stock data.
"""

import logging
import json
import time
import sys
import os
from datetime import datetime, timedelta
from kafka import KafkaConsumer
import pandas as pd
import numpy as np
import requests
from config import (
    KAFKA_BROKER, STOCK_PRICES_TOPIC, TRADING_ALERTS_TOPIC,
    API_KEY, API_BASE_URL, TRADING_STRATEGIES, SYMBOLS_TO_TRACK
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trading-bot')

class TradingBot:
    """Trading bot for analyzing stock data and generating trading signals."""
    
    def __init__(self):
        """Initialize the trading bot."""
        self.stock_data = {}  # Store recent stock data for each symbol
        self.signals = {}     # Store generated trading signals
        self.connect_to_kafka()
        
        # Initialize data structures for each symbol
        for symbol in SYMBOLS_TO_TRACK:
            self.stock_data[symbol] = []
            self.signals[symbol] = []
            
        logger.info(f"Trading bot initialized for symbols: {SYMBOLS_TO_TRACK}")
    
    def connect_to_kafka(self):
        """Connect to Kafka broker and subscribe to topics."""
        try:
            self.consumer = KafkaConsumer(
                STOCK_PRICES_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                auto_offset_reset='latest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='trading-bot-group'
            )
            logger.info(f"Connected to Kafka broker at {KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def fetch_historical_data(self, symbol, days=30):
        """Fetch historical data for initial analysis."""
        try:
            url = f"{API_BASE_URL}/stock/{symbol}/chart/{days}d?token={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(data)
            logger.info(f"Fetched {len(df)} historical data points for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def process_message(self, message):
        """Process incoming Kafka message."""
        try:
            data = message.value
            symbol = data.get('symbol')
            
            if symbol not in SYMBOLS_TO_TRACK:
                return
            
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = int(time.time())
            
            # Store data for the symbol
            self.stock_data[symbol].append(data)
            
            # Keep only recent data (last 100 points)
            if len(self.stock_data[symbol]) > 100:
                self.stock_data[symbol] = self.stock_data[symbol][-100:]
            
            # Generate trading signals
            self.analyze_data(symbol)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def analyze_data(self, symbol):
        """Analyze stock data and generate trading signals."""
        if len(self.stock_data[symbol]) < 20:  # Need enough data points
            return
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(self.stock_data[symbol])
        
        # Apply trading strategies
        signals = []
        
        for strategy_name, strategy_config in TRADING_STRATEGIES.items():
            if strategy_name == 'moving_average_crossover':
                signal = self.moving_average_crossover_strategy(
                    df, 
                    strategy_config['short_window'], 
                    strategy_config['long_window']
                )
                if signal:
                    signals.append({
                        'strategy': strategy_name,
                        'signal': signal,
                        'timestamp': int(time.time())
                    })
            
            elif strategy_name == 'rsi':
                signal = self.rsi_strategy(
                    df, 
                    strategy_config['window'], 
                    strategy_config['overbought'], 
                    strategy_config['oversold']
                )
                if signal:
                    signals.append({
                        'strategy': strategy_name,
                        'signal': signal,
                        'timestamp': int(time.time())
                    })
            
            elif strategy_name == 'bollinger_bands':
                signal = self.bollinger_bands_strategy(
                    df, 
                    strategy_config['window'], 
                    strategy_config['num_std']
                )
                if signal:
                    signals.append({
                        'strategy': strategy_name,
                        'signal': signal,
                        'timestamp': int(time.time())
                    })
        
        # Process generated signals
        for signal in signals:
            self.process_signal(symbol, signal)
    
    def moving_average_crossover_strategy(self, df, short_window, long_window):
        """
        Moving Average Crossover Strategy
        
        Buy signal: Short MA crosses above Long MA
        Sell signal: Short MA crosses below Long MA
        """
        if len(df) < long_window:
            return None
        
        # Calculate moving averages
        df['short_ma'] = df['price'].rolling(window=short_window).mean()
        df['long_ma'] = df['price'].rolling(window=long_window).mean()
        
        # Check for crossover
        if len(df) < 2:
            return None
            
        # Current state
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Check for buy signal (short MA crosses above long MA)
        if (previous['short_ma'] <= previous['long_ma']) and (current['short_ma'] > current['long_ma']):
            return 'buy'
        
        # Check for sell signal (short MA crosses below long MA)
        elif (previous['short_ma'] >= previous['long_ma']) and (current['short_ma'] < current['long_ma']):
            return 'sell'
        
        return None
    
    def rsi_strategy(self, df, window, overbought, oversold):
        """
        Relative Strength Index (RSI) Strategy
        
        Buy signal: RSI below oversold threshold
        Sell signal: RSI above overbought threshold
        """
        if len(df) < window + 1:
            return None
        
        # Calculate RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Check for signals
        current_rsi = df['rsi'].iloc[-1]
        
        if current_rsi <= oversold:
            return 'buy'
        elif current_rsi >= overbought:
            return 'sell'
        
        return None
    
    def bollinger_bands_strategy(self, df, window, num_std):
        """
        Bollinger Bands Strategy
        
        Buy signal: Price crosses below lower band
        Sell signal: Price crosses above upper band
        """
        if len(df) < window:
            return None
        
        # Calculate Bollinger Bands
        df['sma'] = df['price'].rolling(window=window).mean()
        df['std'] = df['price'].rolling(window=window).std()
        df['upper_band'] = df['sma'] + (df['std'] * num_std)
        df['lower_band'] = df['sma'] - (df['std'] * num_std)
        
        # Check for signals
        if len(df) < 2:
            return None
            
        # Current state
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Check for buy signal (price crosses below lower band)
        if (previous['price'] >= previous['lower_band']) and (current['price'] < current['lower_band']):
            return 'buy'
        
        # Check for sell signal (price crosses above upper band)
        elif (previous['price'] <= previous['upper_band']) and (current['price'] > current['upper_band']):
            return 'sell'
        
        return None
    
    def process_signal(self, symbol, signal):
        """Process and store trading signal."""
        # Add symbol to signal
        signal['symbol'] = symbol
        
        # Store signal
        self.signals[symbol].append(signal)
        
        # Keep only recent signals (last 20)
        if len(self.signals[symbol]) > 20:
            self.signals[symbol] = self.signals[symbol][-20:]
        
        # Log signal
        logger.info(f"Generated {signal['signal']} signal for {symbol} using {signal['strategy']} strategy")
        
        # Here you would typically send the signal to a Kafka topic
        # or execute a trade via a brokerage API
        
    def run(self):
        """Main loop to process messages and generate signals."""
        logger.info("Starting trading bot")
        
        try:
            # Process Kafka messages
            for message in self.consumer:
                self.process_message(message)
                
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Error in trading bot: {e}")
        finally:
            if hasattr(self, 'consumer'):
                self.consumer.close()
                logger.info("Kafka consumer closed")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
