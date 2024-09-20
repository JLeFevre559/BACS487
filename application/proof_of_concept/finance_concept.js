const ticker = 'NVDA';
const apiUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?range=1mo&interval=1d`;
console.log("Concept test started");
console.log("API URL: ", apiUrl);
fetch(apiUrl)
  .then(response => response.json())
  .then(data => {
    console.log(data.chart.result[0]); // Stock data for the past month
  })
  .catch(error => console.error('Error fetching stock data:', error));
