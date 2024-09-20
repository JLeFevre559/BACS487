import yfinance as yf
import datetime

# Define the stock ticker symbol (NVIDIA)
ticker_symbol = 'NVDA'

# Get the current date
end_date = datetime.datetime.now()

# Get the date one month ago
start_date = end_date - datetime.timedelta(days=30)

# Download the stock data
nvidia_stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

# Display the stock data
print(nvidia_stock_data)
