-- Initialize Stock Market Data Engineering Database Schema

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Create stock_prices table
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    volume NUMERIC(20, 2),
    timestamp TIMESTAMP NOT NULL,
    fetch_timestamp BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create hypertable for time-series data
SELECT create_hypertable('stock_prices', 'timestamp', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_timestamp ON stock_prices(timestamp);
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_timestamp ON stock_prices(symbol, timestamp);

-- Create stock_metrics table for stream processing results
CREATE TABLE IF NOT EXISTS stock_metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    avg_price NUMERIC(10, 2),
    max_price NUMERIC(10, 2),
    min_price NUMERIC(10, 2),
    avg_volume NUMERIC(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for stock_metrics
CREATE INDEX IF NOT EXISTS idx_stock_metrics_symbol ON stock_metrics(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_metrics_window ON stock_metrics(window_start, window_end);
CREATE INDEX IF NOT EXISTS idx_stock_metrics_symbol_window ON stock_metrics(symbol, window_start, window_end);

-- Create daily_aggregates table for batch processing results
CREATE TABLE IF NOT EXISTS stock_daily_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    avg_price NUMERIC(10, 2),
    max_price NUMERIC(10, 2),
    min_price NUMERIC(10, 2),
    total_volume NUMERIC(20, 2),
    data_points INTEGER,
    price_change NUMERIC(10, 2),
    price_change_pct NUMERIC(10, 2),
    ma_5d NUMERIC(10, 2),
    ma_20d NUMERIC(10, 2),
    ma_50d NUMERIC(10, 2),
    trend VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_symbol_date UNIQUE (symbol, date)
);

-- Create indexes for daily_aggregates
CREATE INDEX IF NOT EXISTS idx_daily_aggregates_symbol ON stock_daily_aggregates(symbol);
CREATE INDEX IF NOT EXISTS idx_daily_aggregates_date ON stock_daily_aggregates(date);
CREATE INDEX IF NOT EXISTS idx_daily_aggregates_symbol_date ON stock_daily_aggregates(symbol, date);

-- Create weekly_aggregates table
CREATE TABLE IF NOT EXISTS stock_weekly_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    year_week VARCHAR(8) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    avg_price NUMERIC(10, 2),
    max_price NUMERIC(10, 2),
    min_price NUMERIC(10, 2),
    total_volume NUMERIC(20, 2),
    data_points INTEGER,
    price_change NUMERIC(10, 2),
    price_change_pct NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_symbol_yearweek UNIQUE (symbol, year_week)
);

-- Create indexes for weekly_aggregates
CREATE INDEX IF NOT EXISTS idx_weekly_aggregates_symbol ON stock_weekly_aggregates(symbol);
CREATE INDEX IF NOT EXISTS idx_weekly_aggregates_yearweek ON stock_weekly_aggregates(year_week);

-- Create monthly_aggregates table
CREATE TABLE IF NOT EXISTS stock_monthly_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    avg_price NUMERIC(10, 2),
    max_price NUMERIC(10, 2),
    min_price NUMERIC(10, 2),
    total_volume NUMERIC(20, 2),
    data_points INTEGER,
    price_change NUMERIC(10, 2),
    price_change_pct NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_symbol_yearmonth UNIQUE (symbol, year_month)
);

-- Create indexes for monthly_aggregates
CREATE INDEX IF NOT EXISTS idx_monthly_aggregates_symbol ON stock_monthly_aggregates(symbol);
CREATE INDEX IF NOT EXISTS idx_monthly_aggregates_yearmonth ON stock_monthly_aggregates(year_month);

-- Create trading_signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    signal VARCHAR(10) NOT NULL,
    price NUMERIC(10, 2),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for trading_signals
CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_signals_timestamp ON trading_signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_trading_signals_strategy ON trading_signals(strategy);

-- Create symbols table to store metadata about tracked stocks
CREATE TABLE IF NOT EXISTS symbols (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(100),
    sector VARCHAR(50),
    industry VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some initial symbols
INSERT INTO symbols (symbol, company_name, sector, industry)
VALUES 
    ('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics'),
    ('MSFT', 'Microsoft Corporation', 'Technology', 'Software'),
    ('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information'),
    ('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail'),
    ('META', 'Meta Platforms Inc.', 'Technology', 'Internet Content & Information'),
    ('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers'),
    ('NVDA', 'NVIDIA Corporation', 'Technology', 'Semiconductors'),
    ('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks'),
    ('V', 'Visa Inc.', 'Financial Services', 'Credit Services'),
    ('WMT', 'Walmart Inc.', 'Consumer Defensive', 'Discount Stores')
ON CONFLICT (symbol) DO NOTHING;

-- Create users and permissions
-- Note: In a production environment, you would use more secure passwords
CREATE USER IF NOT EXISTS reader WITH PASSWORD 'reader_password';
CREATE USER IF NOT EXISTS writer WITH PASSWORD 'writer_password';
CREATE USER IF NOT EXISTS admin WITH PASSWORD 'admin_password';

-- Grant appropriate permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO reader;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO writer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO writer;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
