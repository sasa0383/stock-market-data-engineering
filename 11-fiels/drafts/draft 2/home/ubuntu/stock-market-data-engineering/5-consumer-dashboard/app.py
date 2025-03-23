#!/usr/bin/env python3
"""
Dashboard Application for Stock Market Data Engineering Project
Serves real-time stock analysis via API & UI.
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dashboard')

# Create FastAPI app
app = FastAPI(title="Stock Market Dashboard API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "stockdata")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the dashboard homepage."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stocks", response_model=List[str])
async def get_stocks():
    """Get list of available stock symbols."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol")
        stocks = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return stocks
    except Exception as e:
        logger.error(f"Error fetching stock list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, days: int = 30):
    """Get stock data for a specific symbol."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query for stock data
        cursor.execute(
            """
            SELECT * FROM stock_prices 
            WHERE symbol = %s AND timestamp >= %s
            ORDER BY timestamp
            """,
            (symbol, start_date)
        )
        
        stock_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to list of dicts for JSON serialization
        result = [dict(row) for row in stock_data]
        
        return result
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/aggregates/daily/{symbol}")
async def get_daily_aggregates(symbol: str, days: int = 30):
    """Get daily aggregated data for a specific symbol."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query for daily aggregates
        cursor.execute(
            """
            SELECT * FROM stock_daily_aggregates 
            WHERE symbol = %s AND date >= %s
            ORDER BY date
            """,
            (symbol, start_date)
        )
        
        daily_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to list of dicts for JSON serialization
        result = [dict(row) for row in daily_data]
        
        return result
    except Exception as e:
        logger.error(f"Error fetching daily aggregates for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/trends")
async def get_market_trends(days: int = 7):
    """Get overall market trends."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query for market trends
        cursor.execute(
            """
            SELECT date, 
                   AVG(avg_price) as market_avg_price,
                   COUNT(*) as stock_count,
                   SUM(CASE WHEN trend = 'uptrend' THEN 1 ELSE 0 END) as uptrend_count,
                   SUM(CASE WHEN trend = 'downtrend' THEN 1 ELSE 0 END) as downtrend_count,
                   SUM(CASE WHEN trend = 'sideways' THEN 1 ELSE 0 END) as sideways_count
            FROM stock_daily_aggregates
            WHERE date >= %s
            GROUP BY date
            ORDER BY date
            """,
            (start_date,)
        )
        
        trend_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to list of dicts for JSON serialization
        result = [dict(row) for row in trend_data]
        
        return result
    except Exception as e:
        logger.error(f"Error fetching market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/price")
async def get_price_alerts(threshold: float = 5.0):
    """Get price movement alerts exceeding threshold percentage."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Query for significant price movements
        cursor.execute(
            """
            SELECT symbol, date, avg_price, price_change_pct, trend
            FROM stock_daily_aggregates
            WHERE ABS(price_change_pct) >= %s
            ORDER BY date DESC, ABS(price_change_pct) DESC
            LIMIT 20
            """,
            (threshold,)
        )
        
        alerts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to list of dicts for JSON serialization
        result = [dict(row) for row in alerts]
        
        return result
    except Exception as e:
        logger.error(f"Error fetching price alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
