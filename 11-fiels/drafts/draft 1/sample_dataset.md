# Sample Dataset Research

## Stock Market Dataset from Kaggle

### Overview
- **Dataset Name**: Stock Market Dataset
- **Source**: Kaggle (https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset)
- **Size**: 548 MB
- **Content**: Historical daily prices for all tickers currently trading on NASDAQ
- **Time Range**: Up to April 1, 2020
- **Update Frequency**: Quarterly (as indicated on Kaggle)
- **License**: CC0: Public Domain

### Data Structure
The data for every symbol is saved in CSV format with the following common fields:
- **Date** - specifies trading date (timestamp requirement satisfied)
- **Open** - opening price
- **High** - maximum price during the day
- **Low** - minimum price during the day
- **Close** - close price adjusted for splits
- **Adj Close** - adjusted close price adjusted for both dividends and splits
- **Volume** - the number of shares that changed hands during a given day

### Organization
- Data is organized into two main folders:
  - **ETFs**: Contains CSV files for Exchange Traded Funds
  - **Stocks**: Contains CSV files for individual stocks
- Each filename corresponds to the ticker symbol
- Additional metadata is available in `symbols_valid_meta.csv`

### Suitability for Our Project
1. **Data Volume**: 
   - With all tickers on NASDAQ (over 3,000 stocks), each with daily data points across multiple years, this dataset easily exceeds our 1 million data points requirement.
   - The 548 MB size indicates substantial data volume.

2. **Time-Referenced Data**:
   - Each data point includes a date timestamp, satisfying our requirement for time-referenced data.

3. **Data Quality**:
   - Data is sourced from Yahoo Finance, a reliable financial data provider.
   - The dataset is well-structured and in a standard CSV format.

4. **Accessibility**:
   - Freely available under CC0: Public Domain license.
   - Can be downloaded directly or accessed via Kaggle API.

5. **Extensibility**:
   - The dataset can be extended with more recent data by running the provided data collection script.
   - Additional financial indicators can be calculated from the provided price data.

### Proposed Usage in Our System
1. **Data Ingestion**:
   - Initial bulk ingestion of historical data
   - Scheduled quarterly updates for new data

2. **Data Processing**:
   - Clean and validate data (handle missing values, outliers)
   - Calculate additional financial indicators (moving averages, RSI, MACD)
   - Aggregate data at different time intervals (weekly, monthly)

3. **Data Storage**:
   - Store raw data in distributed file system
   - Store processed data in time-series database

4. **Data Delivery**:
   - Provide aggregated data for machine learning model training
   - Support queries for specific time periods and tickers

### Conclusion
The Stock Market Dataset from Kaggle is an excellent fit for our batch-processing data architecture project. It satisfies all our requirements:
- Large volume (>1 million data points)
- Time-referenced data (daily timestamps)
- High-quality, well-structured data
- Freely available and easily accessible

This dataset will allow us to demonstrate all aspects of our batch-processing architecture, from ingestion to storage, processing, and delivery.
