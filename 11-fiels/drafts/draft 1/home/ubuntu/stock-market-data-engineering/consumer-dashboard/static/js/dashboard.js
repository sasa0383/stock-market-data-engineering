// dashboard.js - Main JavaScript for Stock Market Dashboard

// Global variables
let priceChart = null;
let volumeChart = null;
let currentSymbol = null;
let currentTimeframe = '1d';

// DOM elements
const stockSelector = document.getElementById('stockSelector');
const timeframeSelector = document.getElementById('timeframeSelector');
const stockTitle = document.getElementById('stockTitle');
const priceMetricsTable = document.getElementById('priceMetrics');
const movingAveragesTable = document.getElementById('movingAverages');
const topGainersDiv = document.getElementById('topGainers');
const topLosersDiv = document.getElementById('topLosers');
const mostActiveDiv = document.getElementById('mostActive');

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Load available stocks
    fetchStocks();
    
    // Load market summary
    fetchMarketSummary();
    
    // Set up event listeners
    stockSelector.addEventListener('change', handleStockChange);
    timeframeSelector.addEventListener('change', handleTimeframeChange);
    
    // Set up auto-refresh
    setInterval(refreshData, 60000); // Refresh every minute
});

// Fetch available stocks
async function fetchStocks() {
    try {
        const response = await fetch('/api/stocks');
        const data = await response.json();
        
        // Populate stock selector
        data.stocks.forEach(symbol => {
            const option = document.createElement('option');
            option.value = symbol;
            option.textContent = symbol;
            stockSelector.appendChild(option);
        });
        
        // If we have stocks, select the first one
        if (data.stocks.length > 0) {
            stockSelector.value = data.stocks[0];
            currentSymbol = data.stocks[0];
            loadStockData(currentSymbol, currentTimeframe);
        }
    } catch (error) {
        console.error('Error fetching stocks:', error);
    }
}

// Fetch market summary
async function fetchMarketSummary() {
    try {
        const response = await fetch('/api/market-summary');
        const data = await response.json();
        
        // Populate top gainers
        topGainersDiv.innerHTML = '';
        data.gainers.forEach(stock => {
            const item = document.createElement('div');
            item.className = 'summary-item';
            item.innerHTML = `
                <span>${stock.symbol}</span>
                <span class="positive">+${stock.percent_change.toFixed(2)}%</span>
            `;
            topGainersDiv.appendChild(item);
        });
        
        // Populate top losers
        topLosersDiv.innerHTML = '';
        data.losers.forEach(stock => {
            const item = document.createElement('div');
            item.className = 'summary-item';
            item.innerHTML = `
                <span>${stock.symbol}</span>
                <span class="negative">${stock.percent_change.toFixed(2)}%</span>
            `;
            topLosersDiv.appendChild(item);
        });
        
        // Populate most active
        mostActiveDiv.innerHTML = '';
        data.most_active.forEach(stock => {
            const item = document.createElement('div');
            item.className = 'summary-item';
            const changeClass = stock.percent_change >= 0 ? 'positive' : 'negative';
            const changePrefix = stock.percent_change >= 0 ? '+' : '';
            item.innerHTML = `
                <span>${stock.symbol}</span>
                <span>Vol: ${formatNumber(stock.volume)}</span>
                <span class="${changeClass}">${changePrefix}${stock.percent_change.toFixed(2)}%</span>
            `;
            mostActiveDiv.appendChild(item);
        });
    } catch (error) {
        console.error('Error fetching market summary:', error);
    }
}

// Load stock data
async function loadStockData(symbol, period) {
    try {
        // Update title
        stockTitle.textContent = `${symbol} Stock Details`;
        
        // Fetch stock data
        const response = await fetch(`/api/stock/${symbol}?period=${period}`);
        const data = await response.json();
        
        if (data.data.length === 0) {
            console.error('No data available for this stock and period');
            return;
        }
        
        // Prepare chart data
        const dates = data.data.map(item => new Date(item.date).toLocaleDateString());
        const prices = data.data.map(item => item.close);
        const volumes = data.data.map(item => item.volume);
        
        // Update price chart
        updatePriceChart(dates, prices, symbol);
        
        // Update volume chart
        updateVolumeChart(dates, volumes, symbol);
        
        // Update metrics
        updateMetrics(data.data);
        
        // Fetch moving averages
        fetchMovingAverages(symbol);
    } catch (error) {
        console.error('Error loading stock data:', error);
    }
}

// Update price chart
function updatePriceChart(dates, prices, symbol) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (priceChart) {
        priceChart.destroy();
    }
    
    // Create new chart
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: `${symbol} Price`,
                data: prices,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                pointRadius: 1,
                pointHoverRadius: 5,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${symbol} Price History`
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price ($)'
                    },
                    beginAtZero: false
                }
            }
        }
    });
}

// Update volume chart
function updateVolumeChart(dates, volumes, symbol) {
    const ctx = document.getElementById('volumeChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (volumeChart) {
        volumeChart.destroy();
    }
    
    // Create new chart
    volumeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: `${symbol} Volume`,
                data: volumes,
                backgroundColor: 'rgba(231, 76, 60, 0.7)',
                borderColor: '#e74c3c',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${symbol} Trading Volume`
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Volume'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

// Update metrics table
function updateMetrics(data) {
    // Get the latest data point
    const latest = data[data.length - 1];
    
    // Calculate some basic metrics
    const open = latest.open;
    const close = latest.close;
    const high = latest.high;
    const low = latest.low;
    const change = close - open;
    const changePercent = (change / open) * 100;
    const range = high - low;
    const rangePercent = (range / low) * 100;
    
    // Update price metrics table
    priceMetricsTable.innerHTML = `
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Open</td>
            <td>$${open.toFixed(2)}</td>
        </tr>
        <tr>
            <td>Close</td>
            <td>$${close.toFixed(2)}</td>
        </tr>
        <tr>
            <td>High</td>
            <td>$${high.toFixed(2)}</td>
        </tr>
        <tr>
            <td>Low</td>
            <td>$${low.toFixed(2)}</td>
        </tr>
        <tr>
            <td>Change</td>
            <td class="${change >= 0 ? 'positive' : 'negative'}">${change >= 0 ? '+' : ''}$${change.toFixed(2)} (${changePercent.toFixed(2)}%)</td>
        </tr>
        <tr>
            <td>Range</td>
            <td>$${range.toFixed(2)} (${rangePercent.toFixed(2)}%)</td>
        </tr>
        <tr>
            <td>Volume</td>
            <td>${formatNumber(latest.volume)}</td>
        </tr>
    `;
}

// Fetch moving averages
async function fetchMovingAverages(symbol) {
    try {
        const response = await fetch(`/api/moving-averages/${symbol}`);
        const data = await response.json();
        
        if (data.data.length === 0) {
            console.error('No moving average data available');
            return;
        }
        
        // Get the latest data point
        const latest = data.data[0];
        
        // Update moving averages table
        movingAveragesTable.innerHTML = `
            <tr>
                <th>Period</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>7-Day MA</td>
                <td>$${latest.ma_7day ? latest.ma_7day.toFixed(2) : 'N/A'}</td>
            </tr>
            <tr>
                <td>30-Day MA</td>
                <td>$${latest.ma_30day ? latest.ma_30day.toFixed(2) : 'N/A'}</td>
            </tr>
            <tr>
                <td>90-Day MA</td>
                <td>$${latest.ma_90day ? latest.ma_90day.toFixed(2) : 'N/A'}</td>
            </tr>
        `;
    } catch (error) {
        console.error('Error fetching moving averages:', error);
    }
}

// Handle stock change
function handleStockChange() {
    currentSymbol = stockSelector.value;
    loadStockData(currentSymbol, currentTimeframe);
}

// Handle timeframe change
function handleTimeframeChange() {
    currentTimeframe = timeframeSelector.value;
    if (currentSymbol) {
        loadStockData(currentSymbol, currentTimeframe);
    }
}

// Refresh data
function refreshData() {
    if (currentSymbol) {
        loadStockData(currentSymbol, currentTimeframe);
    }
    fetchMarketSummary();
}

// Format large numbers
function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}
