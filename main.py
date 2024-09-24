import os
import yfinance as yf
import matplotlib.pyplot as plt
import argparse
import http.client, urllib
import pandas as pd
from datetime import datetime, timedelta

# Read API keys and symbol from environment variables
PUSHOVER_TOKEN = os.environ.get('PUSHOVER_TOKEN')
PUSHOVER_USER = os.environ.get('PUSHOVER_USER')
SYMBOL = os.environ.get('STOCK_SYMBOL', '^GSPC')  # Default to S&P 500 if not specified

def get_stock_data(symbol):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    return data

def calculate_sma(data, window):
    return data['Close'].rolling(window=window, min_periods=window).mean()

def send_pushover_notification(title, message):
    print(f"Sending Pushover notification:\nTitle: {title}\nMessage: {message}")  # Debug
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        print("Error: Pushover API key or user key not set in environment variables.")
        return

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "title": title,
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    response = conn.getresponse()
    print(f"Pushover API response: {response.status} {response.reason}")  # Debug

def main(show_chart):
    print(f"Fetching data for symbol: {SYMBOL}")  # Debug
    data = get_stock_data(SYMBOL)

    print("Calculating SMA(200)...")  # Debug
    data['SMA200'] = calculate_sma(data, 200)

    data = data.dropna()

    current_close = data['Close'].iloc[-1]
    current_sma200 = data['SMA200'].iloc[-1]
    current_date = data.index[-1].strftime('%Y-%m-%d')

    print(f"Current date: {current_date}")  # Debug
    print(f"Current closing value: {current_close:.2f}")  # Debug
    print(f"Current SMA(200): {current_sma200:.2f}")  # Debug

    notification_title = f"{SYMBOL} Update"
    notification_body = (f"Symbol: {SYMBOL}\n"
                         f"Date: {current_date}\n"
                         f"Current Closing Value: {current_close:.2f}\n"
                         f"Current SMA(200): {current_sma200:.2f}")

    if current_sma200 < 200:
        notification_body += f"\nAlert: SMA(200) is under 200!"

    send_pushover_notification(notification_title, notification_body)

    if show_chart:
        print("Generating chart...")  # Debug
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data['Close'], label='Close Value')
        plt.plot(data.index, data['SMA200'], label='SMA(200)')
        plt.title(f'{SYMBOL} Value and SMA(200)')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stock Analysis Script')
    parser.add_argument('--chart', type=str, default='false', help='Show chart (true/false)')
    args = parser.parse_args()
    show_chart = args.chart.lower() == 'true'

    print("Starting Stock Analysis Script...")  # Debug
    main(show_chart)
    print("Script execution completed.")  # Debug

