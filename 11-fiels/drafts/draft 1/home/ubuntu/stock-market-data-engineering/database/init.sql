-- Initialize Stock Market Database Schema

-- Create stock_prices table
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp BIGINT NOT NULL,
    date TIMESTAMP NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and date for faster queries
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices (symbol, date);

-- Create trading_signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(10) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and timestamp for trading signals
CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol_timestamp ON trading_signals (symbol, timestamp);

-- Create stock_daily_aggregates table
CREATE TABLE IF NOT EXISTS stock_daily_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    avg_open NUMERIC(10, 2) NOT NULL,
    avg_close NUMERIC(10, 2) NOT NULL,
    max_high NUMERIC(10, 2) NOT NULL,
    min_low NUMERIC(10, 2) NOT NULL,
    total_volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and date for daily aggregates
CREATE INDEX IF NOT EXISTS idx_stock_daily_aggregates_symbol_date ON stock_daily_aggregates (symbol, date);

-- Create stock_weekly_aggregates table
CREATE TABLE IF NOT EXISTS stock_weekly_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    avg_close NUMERIC(10, 2) NOT NULL,
    max_high NUMERIC(10, 2) NOT NULL,
    min_low NUMERIC(10, 2) NOT NULL,
    total_volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and week_start for weekly aggregates
CREATE INDEX IF NOT EXISTS idx_stock_weekly_aggregates_symbol_week ON stock_weekly_aggregates (symbol, week_start);

-- Create stock_monthly_aggregates table
CREATE TABLE IF NOT EXISTS stock_monthly_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    month_start DATE NOT NULL,
    month_end DATE NOT NULL,
    avg_close NUMERIC(10, 2) NOT NULL,
    max_high NUMERIC(10, 2) NOT NULL,
    min_low NUMERIC(10, 2) NOT NULL,
    total_volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and month_start for monthly aggregates
CREATE INDEX IF NOT EXISTS idx_stock_monthly_aggregates_symbol_month ON stock_monthly_aggregates (symbol, month_start);

-- Create stock_moving_averages table
CREATE TABLE IF NOT EXISTS stock_moving_averages (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    ma_7day NUMERIC(10, 2),
    ma_30day NUMERIC(10, 2),
    ma_90day NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and date for moving averages
CREATE INDEX IF NOT EXISTS idx_stock_moving_averages_symbol_date ON stock_moving_averages (symbol, date);

-- Create users table for dashboard authentication (future use)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_preferences table (future use)
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    watchlist JSONB,
    default_timeframe VARCHAR(10) DEFAULT '1d',
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample stock symbols (for testing)
INSERT INTO stock_prices (symbol, timestamp, date, open, high, low, close, volume)
VALUES 
    ('AAPL', 1647360000, '2022-03-15 16:00:00', 155.23, 157.82, 154.46, 157.12, 76532100),
    ('MSFT', 1647360000, '2022-03-15 16:00:00', 280.34, 284.97, 279.12, 283.87, 32654700),
    ('GOOGL', 1647360000, '2022-03-15 16:00:00', 2580.45, 2605.87, 2570.23, 2600.12, 1876500),
    ('AMZN', 1647360000, '2022-03-15 16:00:00', 2910.23, 2945.78, 2900.56, 2932.45, 3456700),
    ('TSLA', 1647360000, '2022-03-15 16:00:00', 780.45, 805.67, 775.23, 801.89, 25678900)
ON CONFLICT DO NOTHING;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;
