#!/usr/bin/env python3
"""
Dashboard App for Stock Market Data Engineering Project
Serves real-time stock analysis via FastAPI
"""

import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import psycopg2
import psycopg2.extras
import json
from datetime import datetime, timedelta
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Stock Market Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the dashboard home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stocks")
async def get_stocks():
    """Get list of available stock symbols"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol")
            stocks = [row['symbol'] for row in cur.fetchall()]
            return {"stocks": stocks}
    except Exception as e:
        logger.error(f"Error fetching stocks: {e}")
        raise HTTPException(status_code=500, detail="Error fetching stocks")
    finally:
        conn.close()

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, period: str = "1d"):
    """Get stock data for a specific symbol and time period"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Calculate date range based on period
            end_date = datetime.now()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "1w":
                start_date = end_date - timedelta(weeks=1)
            elif period == "1m":
                start_date = end_date - timedelta(days=30)
            elif period == "3m":
                start_date = end_date - timedelta(days=90)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=1)
            
            # Query database
            cur.execute(
                """
                SELECT symbol, date, open, high, low, close, volume 
                FROM stock_prices 
                WHERE symbol = %s AND date BETWEEN %s AND %s
                ORDER BY date
                """,
                (symbol, start_date, end_date)
            )
            
            # Format results
            results = []
            for row in cur.fetchall():
                results.append({
                    "symbol": row['symbol'],
                    "date": row['date'].isoformat(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume'])
                })
            
            return {"data": results}
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching stock data")
    finally:
        conn.close()

@app.get("/api/aggregates/{symbol}")
async def get_stock_aggregates(symbol: str, period: str = "daily"):
    """Get stock aggregates for a specific symbol and period type"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Determine table based on period
            if period == "daily":
                table = "stock_daily_aggregates"
            elif period == "weekly":
                table = "stock_weekly_aggregates"
            elif period == "monthly":
                table = "stock_monthly_aggregates"
            else:
                table = "stock_daily_aggregates"
            
            # Query database
            cur.execute(
                f"""
                SELECT * FROM {table}
                WHERE symbol = %s
                ORDER BY date DESC
                LIMIT 30
                """,
                (symbol,)
            )
            
            # Format results
            results = []
            for row in cur.fetchall():
                result = dict(row)
                # Convert decimal types to float for JSON serialization
                for key, value in result.items():
                    if isinstance(value, (datetime, timedelta)):
                        result[key] = value.isoformat()
                    elif hasattr(value, '__float__'):
                        result[key] = float(value)
                results.append(result)
            
            return {"data": results}
    except Exception as e:
        logger.error(f"Error fetching stock aggregates: {e}")
        raise HTTPException(status_code=500, detail="Error fetching stock aggregates")
    finally:
        conn.close()

@app.get("/api/moving-averages/{symbol}")
async def get_moving_averages(symbol: str):
    """Get moving averages for a specific symbol"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM stock_moving_averages
                WHERE symbol = %s
                ORDER BY date DESC
                LIMIT 90
                """,
                (symbol,)
            )
            
            # Format results
            results = []
            for row in cur.fetchall():
                result = dict(row)
                # Convert decimal types to float for JSON serialization
                for key, value in result.items():
                    if isinstance(value, (datetime, timedelta)):
                        result[key] = value.isoformat()
                    elif hasattr(value, '__float__'):
                        result[key] = float(value)
                results.append(result)
            
            return {"data": results}
    except Exception as e:
        logger.error(f"Error fetching moving averages: {e}")
        raise HTTPException(status_code=500, detail="Error fetching moving averages")
    finally:
        conn.close()

@app.get("/api/market-summary")
async def get_market_summary():
    """Get overall market summary"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Get top gainers
            cur.execute(
                """
                SELECT symbol, 
                       (close - open) / open * 100 as percent_change,
                       close, volume
                FROM stock_prices
                WHERE date = (SELECT MAX(date) FROM stock_prices)
                ORDER BY percent_change DESC
                LIMIT 5
                """
            )
            gainers = []
            for row in cur.fetchall():
                gainers.append({
                    "symbol": row['symbol'],
                    "percent_change": float(row['percent_change']),
                    "price": float(row['close']),
                    "volume": int(row['volume'])
                })
            
            # Get top losers
            cur.execute(
                """
                SELECT symbol, 
                       (close - open) / open * 100 as percent_change,
                       close, volume
                FROM stock_prices
                WHERE date = (SELECT MAX(date) FROM stock_prices)
                ORDER BY percent_change ASC
                LIMIT 5
                """
            )
            losers = []
            for row in cur.fetchall():
                losers.append({
                    "symbol": row['symbol'],
                    "percent_change": float(row['percent_change']),
                    "price": float(row['close']),
                    "volume": int(row['volume'])
                })
            
            # Get most active by volume
            cur.execute(
                """
                SELECT symbol, volume, close,
                       (close - open) / open * 100 as percent_change
                FROM stock_prices
                WHERE date = (SELECT MAX(date) FROM stock_prices)
                ORDER BY volume DESC
                LIMIT 5
                """
            )
            most_active = []
            for row in cur.fetchall():
                most_active.append({
                    "symbol": row['symbol'],
                    "volume": int(row['volume']),
                    "price": float(row['close']),
                    "percent_change": float(row['percent_change'])
                })
            
            return {
                "gainers": gainers,
                "losers": losers,
                "most_active": most_active
            }
    except Exception as e:
        logger.error(f"Error fetching market summary: {e}")
        raise HTTPException(status_code=500, detail="Error fetching market summary")
    finally:
        conn.close()

def main():
    """Main function to run the FastAPI app"""
    import uvicorn
    logger.info("Starting Stock Market Dashboard API")
    uvicorn.run(app, host=config.HOST, port=config.PORT)

if __name__ == "__main__":
    main()
