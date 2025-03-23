# Consumer Dashboard

## Overview
The Consumer Dashboard service provides a web-based interface for visualizing stock market data and analytics. It serves real-time stock analysis via a FastAPI backend and a responsive frontend built with HTML, CSS, and JavaScript.

## Features
- Interactive stock price charts with volume data
- Market trend visualization
- Price movement alerts
- Real-time data updates
- Responsive design for desktop and mobile devices
- RESTful API endpoints for data access

## Components
1. **FastAPI Backend**: Provides API endpoints for stock data
2. **Jinja2 Templates**: Renders HTML templates
3. **Chart.js**: Creates interactive data visualizations
4. **Bootstrap**: Provides responsive UI components

## Requirements
- Python 3.9+
- FastAPI
- Uvicorn
- Jinja2
- PostgreSQL connector

## API Endpoints
- `/api/stocks`: Get list of available stock symbols
- `/api/stock/{symbol}`: Get stock data for a specific symbol
- `/api/aggregates/daily/{symbol}`: Get daily aggregated data
- `/api/market/trends`: Get overall market trends
- `/api/alerts/price`: Get price movement alerts

## Usage
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the service:
   ```
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

3. Access the dashboard:
   ```
   http://localhost:8000
   ```

## Docker Usage
Build the Docker image:
```
docker build -t stock-dashboard .
```

Run the container:
```
docker run -p 8000:8000 --network=stock-market-data-engineering_default stock-dashboard
```

## Data Flow
1. Service connects to PostgreSQL database
2. API endpoints retrieve and format data
3. Frontend JavaScript fetches data from API endpoints
4. Chart.js renders visualizations based on the data
5. User interactions trigger new API requests

## Customization
- Edit `templates/index.html` to modify the dashboard layout
- Edit `static/css/styles.css` to customize the appearance
- Edit `static/js/dashboard.js` to change the behavior
- Modify `app.py` to add new API endpoints or features
