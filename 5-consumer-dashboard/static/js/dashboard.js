// Dashboard JavaScript for Stock Market Dashboard

// Global variables for charts
let priceChart = null;
let marketTrendsChart = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Load list of stocks
    loadStocks();
    
    // Load market trends
    loadMarketTrends();
    
    // Load price alerts
    loadPriceAlerts();
    
    // Set up event listeners
    document.getElementById('stockSelector').addEventListener('change', handleStockSelection);
    document.getElementById('timeRange').addEventListener('change', handleTimeRangeChange);
});

// Load available stocks
async function loadStocks() {
    try {
        const response = await fetch('/api/stocks');
        const stocks = await response.json();
        
        const stockSelector = document.getElementById('stockSelector');
        stockSelector.innerHTML = '<option value="">Select a stock...</option>';
        
        stocks.forEach(symbol => {
            const option = document.createElement('option');
            option.value = symbol;
            option.textContent = symbol;
            stockSelector.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading stocks:', error);
        showError('Failed to load stock list. Please try again later.');
    }
}

// Handle stock selection change
async function handleStockSelection() {
    const symbol = document.getElementById('stockSelector').value;
    const days = document.getElementById('timeRange').value;
    
    if (!symbol) return;
    
    try {
        // Load stock data
        const stockData = await fetchStockData(symbol, days);
        
        // Update stock info
        updateStockInfo(stockData);
        
        // Update price chart
        updatePriceChart(stockData);
    } catch (error) {
        console.error('Error loading stock data:', error);
        showError('Failed to load stock data. Please try again later.');
    }
}

// Handle time range change
function handleTimeRangeChange() {
    const symbol = document.getElementById('stockSelector').value;
    if (symbol) {
        handleStockSelection();
    }
}

// Fetch stock data from API
async function fetchStockData(symbol, days) {
    const response = await fetch(`/api/stock/${symbol}?days=${days}`);
    return await response.json();
}

// Update stock information panel
function updateStockInfo(stockData) {
    if (!stockData || stockData.length === 0) {
        document.getElementById('stockInfo').innerHTML = '<p>No data available for selected stock</p>';
        return;
    }
    
    const latestData = stockData[stockData.length - 1];
    const previousData = stockData.length > 1 ? stockData[stockData.length - 2] : null;
    
    let priceChange = 0;
    let priceChangePercent = 0;
    
    if (previousData) {
        priceChange = latestData.price - previousData.price;
        priceChangePercent = (priceChange / previousData.price) * 100;
    }
    
    const changeClass = priceChange >= 0 ? 'uptrend' : 'downtrend';
    const changeIcon = priceChange >= 0 ? '▲' : '▼';
    
    const html = `
        <h3>${latestData.symbol}</h3>
        <p class="fs-4">$${latestData.price.toFixed(2)} <span class="${changeClass}">${changeIcon} ${Math.abs(priceChange).toFixed(2)} (${Math.abs(priceChangePercent).toFixed(2)}%)</span></p>
        <p>Volume: ${latestData.volume.toLocaleString()}</p>
        <p>Last Updated: ${new Date(latestData.timestamp).toLocaleString()}</p>
    `;
    
    document.getElementById('stockInfo').innerHTML = html;
}

// Update price chart
function updatePriceChart(stockData) {
    if (!stockData || stockData.length === 0) return;
    
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Prepare data
    const labels = stockData.map(data => new Date(data.timestamp).toLocaleDateString());
    const prices = stockData.map(data => data.price);
    const volumes = stockData.map(data => data.volume);
    
    // Destroy existing chart if it exists
    if (priceChart) {
        priceChart.destroy();
    }
    
    // Create new chart
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Price ($)',
                    data: prices,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    yAxisID: 'y'
                },
                {
                    label: 'Volume',
                    data: volumes,
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    type: 'bar',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                    title: {
                        display: true,
                        text: 'Volume'
                    }
                }
            }
        }
    });
}

// Load market trends
async function loadMarketTrends() {
    try {
        const response = await fetch('/api/market/trends');
        const trendData = await response.json();
        
        updateMarketTrendsChart(trendData);
    } catch (error) {
        console.error('Error loading market trends:', error);
    }
}

// Update market trends chart
function updateMarketTrendsChart(trendData) {
    if (!trendData || trendData.length === 0) return;
    
    const ctx = document.getElementById('marketTrendsChart').getContext('2d');
    
    // Prepare data
    const labels = trendData.map(data => new Date(data.date).toLocaleDateString());
    const uptrendCounts = trendData.map(data => data.uptrend_count);
    const downtrendCounts = trendData.map(data => data.downtrend_count);
    const sidewaysCounts = trendData.map(data => data.sideways_count);
    
    // Destroy existing chart if it exists
    if (marketTrendsChart) {
        marketTrendsChart.destroy();
    }
    
    // Create new chart
    marketTrendsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Uptrend',
                    data: uptrendCounts,
                    backgroundColor: 'rgba(40, 167, 69, 0.7)'
                },
                {
                    label: 'Downtrend',
                    data: downtrendCounts,
                    backgroundColor: 'rgba(220, 53, 69, 0.7)'
                },
                {
                    label: 'Sideways',
                    data: sidewaysCounts,
                    backgroundColor: 'rgba(108, 117, 125, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Stocks'
                    }
                }
            }
        }
    });
}

// Load price alerts
async function loadPriceAlerts() {
    try {
        const response = await fetch('/api/alerts/price');
        const alerts = await response.json();
        
        updateAlertsTable(alerts);
    } catch (error) {
        console.error('Error loading price alerts:', error);
    }
}

// Update alerts table
function updateAlertsTable(alerts) {
    const tableBody = document.querySelector('#alertsTable tbody');
    
    if (!alerts || alerts.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No alerts available</td></tr>';
        return;
    }
    
    let html = '';
    
    alerts.forEach(alert => {
        const trendClass = alert.trend === 'uptrend' ? 'uptrend' : (alert.trend === 'downtrend' ? 'downtrend' : 'sideways');
        const changeClass = alert.price_change_pct >= 0 ? 'uptrend' : 'downtrend';
        const changeIcon = alert.price_change_pct >= 0 ? '▲' : '▼';
        
        html += `
            <tr>
                <td>${alert.symbol}</td>
                <td>${new Date(alert.date).toLocaleDateString()}</td>
                <td>$${alert.avg_price.toFixed(2)}</td>
                <td class="${changeClass}">${changeIcon} ${Math.abs(alert.price_change_pct).toFixed(2)}%</td>
                <td class="${trendClass}">${alert.trend}</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

// Show error message
function showError(message) {
    // Could implement a toast or alert system here
    console.error(message);
}
