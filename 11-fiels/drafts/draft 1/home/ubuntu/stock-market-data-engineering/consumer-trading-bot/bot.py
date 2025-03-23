#!/usr/bin/env python3
"""
Trading Bot for Stock Market Data Engineering Project
Implements trading strategies based on real-time stock data
"""

import logging
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from kafka import KafkaConsumer
import psycopg2
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingBot:
    """Trading bot that implements various trading strategies"""
    
    def __init__(self):
        """Initialize the trading bot"""
        self.strategies = {
            'moving_average_crossover': self.moving_average_crossover_strategy,
            'rsi_strategy': self.rsi_strategy,
            'bollinger_bands': self.bollinger_bands_strategy
        }
        self.positions = {}  # Current positions: {symbol: {'quantity': qty, 'entry_price': price}}
        self.signals = []    # Trading signals history
        self.connect_to_kafka()
        self.connect_to_database()
        
    def connect_to_kafka(self):
        """Connect to Kafka broker"""
        try:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC_STOCK_PRICES,
                bootstrap_servers=config.KAFKA_BROKER,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                group_id='trading-bot'
            )
            logger.info(f"Connected to Kafka broker at {config.KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def connect_to_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=config.POSTGRES_HOST,
                database=config.POSTGRES_DB,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD
            )
            logger.info(f"Connected to PostgreSQL database at {config.POSTGRES_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_historical_data(self, symbol, days=30):
        """Get historical data for a symbol from the database"""
        try:
            query = """
                SELECT date, open, high, low, close, volume
                FROM stock_prices
                WHERE symbol = %s
                AND date >= %s
                ORDER BY date
            """
            start_date = datetime.now() - timedelta(days=days)
            
            with self.conn.cursor() as cur:
                cur.execute(query, (symbol, start_date))
                rows = cur.fetchall()
                
                if not rows:
                    logger.warning(f"No historical data found for {symbol}")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                return df
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate technical indicators for a DataFrame"""
        if df is None or len(df) < 30:
            return None
        
        # Calculate moving averages
        df['ma_7'] = df['close'].rolling(window=7).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        # Calculate RSI (Relative Strength Index)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['std_20'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['ma_20'] + (df['std_20'] * 2)
        df['lower_band'] = df['ma_20'] - (df['std_20'] * 2)
        
        return df
    
    def moving_average_crossover_strategy(self, df, current_price):
        """
        Moving Average Crossover Strategy
        Buy when short-term MA crosses above long-term MA
        Sell when short-term MA crosses below long-term MA
        """
        if df is None or len(df) < 20:
            return 'HOLD', None
        
        # Get the last two rows to check for crossover
        last_two = df.iloc[-2:].copy()
        
        # Check for buy signal (7-day MA crosses above 20-day MA)
        if last_two['ma_7'].iloc[0] < last_two['ma_20'].iloc[0] and \
           last_two['ma_7'].iloc[1] > last_two['ma_20'].iloc[1]:
            return 'BUY', {
                'reason': 'MA Crossover: 7-day MA crossed above 20-day MA',
                'ma_7': last_two['ma_7'].iloc[1],
                'ma_20': last_two['ma_20'].iloc[1]
            }
        
        # Check for sell signal (7-day MA crosses below 20-day MA)
        elif last_two['ma_7'].iloc[0] > last_two['ma_20'].iloc[0] and \
             last_two['ma_7'].iloc[1] < last_two['ma_20'].iloc[1]:
            return 'SELL', {
                'reason': 'MA Crossover: 7-day MA crossed below 20-day MA',
                'ma_7': last_two['ma_7'].iloc[1],
                'ma_20': last_two['ma_20'].iloc[1]
            }
        
        return 'HOLD', None
    
    def rsi_strategy(self, df, current_price):
        """
        RSI Strategy
        Buy when RSI is below 30 (oversold)
        Sell when RSI is above 70 (overbought)
        """
        if df is None or len(df) < 14:
            return 'HOLD', None
        
        # Get the latest RSI value
        latest_rsi = df['rsi'].iloc[-1]
        
        # Check for buy signal (RSI below 30)
        if latest_rsi < 30:
            return 'BUY', {
                'reason': 'RSI Strategy: RSI below 30 (oversold)',
                'rsi': latest_rsi
            }
        
        # Check for sell signal (RSI above 70)
        elif latest_rsi > 70:
            return 'SELL', {
                'reason': 'RSI Strategy: RSI above 70 (overbought)',
                'rsi': latest_rsi
            }
        
        return 'HOLD', None
    
    def bollinger_bands_strategy(self, df, current_price):
        """
        Bollinger Bands Strategy
        Buy when price touches lower band
        Sell when price touches upper band
        """
        if df is None or len(df) < 20:
            return 'HOLD', None
        
        # Get the latest values
        latest = df.iloc[-1]
        
        # Check for buy signal (price touches lower band)
        if current_price <= latest['lower_band']:
            return 'BUY', {
                'reason': 'Bollinger Bands: Price touched lower band',
                'price': current_price,
                'lower_band': latest['lower_band']
            }
        
        # Check for sell signal (price touches upper band)
        elif current_price >= latest['upper_band']:
            return 'SELL', {
                'reason': 'Bollinger Bands: Price touched upper band',
                'price': current_price,
                'upper_band': latest['upper_band']
            }
        
        return 'HOLD', None
    
    def execute_trade(self, symbol, action, price, quantity, details=None):
        """Execute a trade (simulated)"""
        timestamp = datetime.now().isoformat()
        
        if action == 'BUY':
            # Update positions
            if symbol in self.positions:
                # Average down/up
                current_qty = self.positions[symbol]['quantity']
                current_price = self.positions[symbol]['entry_price']
                new_qty = current_qty + quantity
                new_price = (current_qty * current_price + quantity * price) / new_qty
                self.positions[symbol] = {'quantity': new_qty, 'entry_price': new_price}
            else:
                # New position
                self.positions[symbol] = {'quantity': quantity, 'entry_price': price}
            
            logger.info(f"BUY: {quantity} shares of {symbol} at ${price:.2f}")
        
        elif action == 'SELL':
            # Update positions
            if symbol in self.positions:
                current_qty = self.positions[symbol]['quantity']
                if quantity >= current_qty:
                    # Close position
                    del self.positions[symbol]
                else:
                    # Partial sell
                    self.positions[symbol]['quantity'] -= quantity
            else:
                logger.warning(f"Attempted to sell {symbol} but no position exists")
                return
            
            logger.info(f"SELL: {quantity} shares of {symbol} at ${price:.2f}")
        
        # Record the signal
        signal = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'price': price,
            'quantity': quantity,
            'details': details
        }
        self.signals.append(signal)
        
        # Publish to Kafka (in a real implementation)
        # self.producer.send(config.KAFKA_TOPIC_TRADING_SIGNALS, signal)
        
        # Store in database (in a real implementation)
        self.store_signal_in_db(signal)
    
    def store_signal_in_db(self, signal):
        """Store a trading signal in the database"""
        try:
            query = """
                INSERT INTO trading_signals
                (timestamp, symbol, action, price, quantity, details)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            with self.conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        signal['timestamp'],
                        signal['symbol'],
                        signal['action'],
                        signal['price'],
                        signal['quantity'],
                        json.dumps(signal['details']) if signal['details'] else None
                    )
                )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error storing signal in database: {e}")
    
    def analyze_stock(self, symbol, price):
        """Analyze a stock and generate trading signals"""
        # Get historical data
        historical_data = self.get_historical_data(symbol)
        
        # Calculate indicators
        df_with_indicators = self.calculate_indicators(historical_data)
        
        if df_with_indicators is None:
            logger.warning(f"Insufficient data to analyze {symbol}")
            return
        
        # Apply each strategy
        signals = {}
        for strategy_name, strategy_func in self.strategies.items():
            if strategy_name in config.ACTIVE_STRATEGIES:
                action, details = strategy_func(df_with_indicators, price)
                signals[strategy_name] = {'action': action, 'details': details}
        
        # Determine final action based on strategy weights
        buy_score = 0
        sell_score = 0
        
        for strategy_name, result in signals.items():
            weight = config.STRATEGY_WEIGHTS.get(strategy_name, 1)
            if result['action'] == 'BUY':
                buy_score += weight
            elif result['action'] == 'SELL':
                sell_score += weight
        
        # Execute trade if score exceeds threshold
        if buy_score >= config.BUY_THRESHOLD and symbol not in self.positions:
            quantity = self.calculate_position_size(symbol, price)
            self.execute_trade(symbol, 'BUY', price, quantity, {
                'strategies': signals,
                'buy_score': buy_score,
                'sell_score': sell_score
            })
        elif sell_score >= config.SELL_THRESHOLD and symbol in self.positions:
            quantity = self.positions[symbol]['quantity']
            self.execute_trade(symbol, 'SELL', price, quantity, {
                'strategies': signals,
                'buy_score': buy_score,
                'sell_score': sell_score
            })
    
    def calculate_position_size(self, symbol, price):
        """Calculate the position size based on risk management rules"""
        # Simple fixed quantity for demonstration
        return config.DEFAULT_QUANTITY
    
    def run(self):
        """Run the trading bot"""
        logger.info("Starting trading bot")
        
        try:
            for message in self.consumer:
                stock_data = message.value
                symbol = stock_data['symbol']
                price = stock_data['close']
                
                logger.info(f"Received data for {symbol}: ${price:.2f}")
                
                # Skip if symbol is not in our watchlist
                if symbol not in config.WATCHLIST:
                    continue
                
                # Analyze the stock
                self.analyze_stock(symbol, price)
                
                # Print current positions
                if self.positions:
                    logger.info(f"Current positions: {self.positions}")
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Error in trading bot: {e}")
        finally:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            logger.info("Trading bot stopped")

def main():
    """Main function to run the trading bot"""
    bot = TradingBot()
    bot.run()

if __name__ == "__main__":
    main()
