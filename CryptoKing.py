import requests
import json
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import numpy as np
from sklearn.linear_model import LinearRegression
import logging
import os

api_key = 'YOUR_API_KEY_HERE'
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key
}

params = {
    "start": 1,
    "limit": 80,
    "convert": "USD"
}


log_file_path = os.path.expanduser("~/Desktop/crypto_analyzer.log")
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def fetch_crypto_data_and_save():
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)  # Add this line to check the content of data
        save_path = os.path.join(os.path.expanduser("~/Documents"), 'crypto_data.txt')
        
        with open(save_path, 'w') as file:
            json.dump(data, file)
        logging.info("Data fetched and saved successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data: {e}")
    except PermissionError as e:
        logging.error(f"Permission error: {e}")


def read_data_from_file(filename=None):
    try:
        if filename is None:
            filename = os.path.join(os.path.expanduser("~/Documents"), 'crypto_data.txt')
        
        with open(filename, 'r') as file:
            data = json.load(file)
        logging.info("Data read from file successfully.")
        return data
    except FileNotFoundError:
        logging.error("Data file not found.")
        return None
    except PermissionError as e:
        logging.error(f"Permission error: {e}")
        return None

def save_previous_prices(previous_prices, filename=None):
    try:
        if filename is None:
            filename = os.path.join(os.path.expanduser("~/Documents"), 'previous_prices.txt')
        
        with open(filename, 'w') as file:
            json.dump(previous_prices, file)
        logging.info("Previous prices saved successfully.")
    except PermissionError as e:
        logging.error(f"Permission error: {e}")

def load_previous_prices(filename=None):
    try:
        if filename is None:
            filename = os.path.join(os.path.expanduser("~/Documents"), 'previous_prices.txt')
        
        with open(filename, 'r') as file:
            previous_prices = json.load(file)
        logging.info("Previous prices loaded successfully.")
        return previous_prices
    except FileNotFoundError:
        logging.error("Previous prices file not found.")
        return {}
    except PermissionError as e:
        logging.error(f"Permission error: {e}")
        return {}
        
def calculate_percentage_change(current_price, previous_price):
    if previous_price == 0:
        return None  # or return 0 or some other default value
    return ((current_price - previous_price) / abs(previous_price)) * 100


def calculate_rsi(prices, window=14):
    deltas = np.diff(prices)
    seed = deltas[:window]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:window] = 100. - 100. / (1. + rs)

    for i in range(window, len(prices)):
        delta = deltas[i - 1]
        upval = delta if delta > 0 else 0
        downval = -delta if delta < 0 else 0
        up = (up * (window - 1) + upval) / window
        down = (down * (window - 1) + downval) / window
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi

def calculate_moving_average(prices, window=14):
    return np.convolve(prices, np.ones(window) / window, mode='valid')

def calculate_ema(prices, window=14):
    if window >= len(prices):
        return np.array([prices[0]] * len(prices))

    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a = np.convolve(prices, weights, mode='full')[:len(prices)]
    a[:window] = a[window]
    return a

def calculate_bollinger_bands(prices, window=20):
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return upper_band, lower_band

def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    ema_short = calculate_ema(prices, short_window)
    ema_long = calculate_ema(prices, long_window)
    macd = ema_short - ema_long
    signal = calculate_ema(macd, signal_window)
    return macd, signal
    
continuously_increasing_coins = set() 

def analyze_data(data, previous_prices):
    try:
        coins = data["data"]
    except KeyError:
        logging.error("Invalid data format: missing 'data' key")
        return [], [], [], []

    if not isinstance(coins, list):
        logging.error("Data is not in the expected format (list of dictionaries)")
        return [], [], [], []

    changes = []
    ditch_coins = []

    for coin in coins:
        name = coin.get('name')
        symbol = coin.get('symbol')
        current_price = coin.get('quote', {}).get('USD', {}).get('price')

        if None in (name, symbol, current_price):
            logging.warning(f"Skipping {name} ({symbol}) due to missing data")
            continue

        if symbol in previous_prices:
            previous_price = previous_prices[symbol]['price']
            percentage_change = calculate_percentage_change(current_price, previous_price)
            changes.append((name, symbol, percentage_change))
            logging.info(f"Change for {name} ({symbol}): {percentage_change:.2f}%")

            if percentage_change < 0:
                previous_prices[symbol]['ditch'] = previous_prices[symbol].get('ditch', 0) + 1
                if previous_prices[symbol]['ditch'] >= 7:
                    ditch_coins.append((name, symbol))
                    previous_prices[symbol]['consecutive_increases'] = 0  # Reset consecutive increases

            if percentage_change >= 0:  # Consider any increase as a consecutive increase
                previous_prices[symbol]['buy'] = previous_prices[symbol].get('buy', 0) + 1
                previous_prices[symbol]['consecutive_increases'] += 1  # Increase consecutive increases
                if previous_prices[symbol]['consecutive_increases'] >= 4:
                    continuously_increasing_coins.add((name, symbol))
            else:
                previous_prices[symbol]['consecutive_increases'] = 0  # Reset consecutive increases if price doesn't increase

        if symbol not in previous_prices:
            previous_prices[symbol] = {'price': current_price, 'changes': [], 'ditch': 0, 'consecutive_increases': 0}

        previous_prices[symbol]['price'] = current_price

    for symbol, data in previous_prices.items():
        data['changes'].append(data['price'])
        if len(data['changes']) > 30:
            data['changes'].pop(0)

        if len(data['changes']) >= 20:
            prices = pd.Series(data['changes'])
            upper_band, lower_band = calculate_bollinger_bands(prices)
            current_price = prices.iloc[-1]
            if current_price <= lower_band.iloc[-1]:
                logging.info(f"{name} ({symbol}) touched or crossed the lower Bollinger Band")

        if len(data['changes']) >= 14:
            rsi = calculate_rsi(data['changes'])
            moving_average = calculate_moving_average(data['changes'])
            macd, signal = calculate_macd(data['changes'])
            logging.info(f"RSI for {symbol}: {rsi[-1]:.2f}")
            logging.info(f"Moving Average for {symbol}: {moving_average[-1]:.2f}")
            logging.info(f"MACD for {symbol}: {macd[-1]:.2f}, Signal: {signal[-1]:.2f}")

    ditch_coins = [(name, symbol) for name, symbol in ditch_coins if symbol in previous_prices]

    changes.sort(key=lambda x: x[2], reverse=True)
    top_5_hot = changes[:5]
    top_5_sell = changes[-5:]

    logging.info("Top 5 HOT: " + str(top_5_hot))
    logging.info("Top 5 SELL: " + str(top_5_sell))

    coins_to_buy = []
    for name, symbol, change in changes:
        reason = ""
        if symbol in previous_prices and len(previous_prices[symbol]['changes']) >= 14:
            rsi = calculate_rsi(previous_prices[symbol]['changes'])
            moving_average = calculate_moving_average(previous_prices[symbol]['changes'])
            macd, signal = calculate_macd(previous_prices[symbol]['changes'])
            if change >= 0.75 or (rsi[-1] < 40 and previous_prices[symbol]['price'] > moving_average[-1] and macd[-1] > signal[-1]):
                reason = "Percentage change >= 0.75% or (RSI < 40 and price > moving average and MACD > Signal)"
            if reason:
                coins_to_buy.append((name, symbol, change, reason))
                if previous_prices[symbol].get('consecutive_increases', 0) >= 4:
                    logging.info(f"{name} ({symbol}) is catching fire!")

    return top_5_hot, top_5_sell, coins_to_buy, ditch_coins
  
alerted_coins = set()

def display_data(top_5_hot, top_5_sell, coins_to_buy, coins_to_ditch):
    global continuously_increasing_coins

    hot_label.config(text="Top 5 | Increasing:")
    sell_label.config(text="Top 5 | Decreasing:")
    buy_label.config(text="Coins to Buy:")
    ditch_label.config(text="Coins to Ditch:")
    hot_text.delete(1.0, tk.END)
    sell_text.delete(1.0, tk.END)
    buy_text.delete(1.0, tk.END)
    ditch_text.delete(1.0, tk.END)

    for name, symbol, change in top_5_hot:
        hot_text.insert(tk.END, f"{name:<20} ({symbol}): {change:>6.2f}%\n")

    for name, symbol, change in top_5_sell:
        sell_text.insert(tk.END, f"{name:<20} ({symbol}): {change:>6.2f}%\n")

    for name, symbol, change, reason in coins_to_buy:
        if (name, symbol) in alerted_coins:
            continue
        
        if (name, symbol) in continuously_increasing_coins:
            buy_text.insert(tk.END, f"{name:<20} ({symbol}): {change:>6.2f}% 🔥 - {reason}\n", 'green')
        else:
            buy_text.insert(tk.END, f"{name:<20} ({symbol}): {change:>6.2f}% - {reason}\n")
        
        alerted_coins.add((name, symbol))
        
        alert_message = f"{name} ({symbol}) has been added to the 'Coins to Buy' list.\nReason: {reason}"
        messagebox.showinfo("Coin Alert", alert_message)

    for name, symbol in coins_to_ditch:
        ditch_text.insert(tk.END, f"{name:<20} ({symbol})\n", 'red')

    continuously_increasing_coins = {(name, symbol) for name, symbol, _, _ in coins_to_buy} - {(name, symbol) for name, symbol in coins_to_ditch}

    hot_text.update_idletasks()
    sell_text.update_idletasks()
    buy_text.update_idletasks()
    ditch_text.update_idletasks()

def update_data():
    logging.info("Updating data...")
    fetch_crypto_data_and_save()
    data = read_data_from_file()
    previous_prices = load_previous_prices()
    if data is not None and previous_prices is not None:
        top_5_hot, top_5_sell, coins_to_buy, ditch_coins = analyze_data(data, previous_prices)
        display_data(top_5_hot, top_5_sell, coins_to_buy, ditch_coins)
        save_previous_prices(previous_prices)  
    root.after(60000, update_data)  # Update every min 300000/5 minutes

root = tk.Tk()
root.title("Crypto King")
root.geometry("725x500")

# Title label
title_label = ttk.Label(root, text="Crypto King", font=("Helvetica", 20, "bold"))
title_label.pack(pady=20)

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 13))
style.configure("TText", font=("Rockwell", 11))

main_frame = ttk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

# Top 5 HOT
hot_frame = ttk.Frame(main_frame)
hot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

hot_label = ttk.Label(hot_frame, text="Top 5 HOT:")
hot_label.pack(anchor="w")
hot_text = tk.Text(hot_frame, height=10, width=40)
hot_text.pack(expand=True, fill="both")

# Top 5 SELL
sell_frame = ttk.Frame(main_frame)
sell_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

sell_label = ttk.Label(sell_frame, text="Top 5 SELL:")
sell_label.pack(anchor="w")
sell_text = tk.Text(sell_frame, height=10, width=40)
sell_text.pack(expand=True, fill="both")

# Coins to Buy
buy_frame = ttk.Frame(main_frame)
buy_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

buy_label = ttk.Label(buy_frame, text="Coins to Buy:")
buy_label.pack(anchor="w")
buy_text = tk.Text(buy_frame, height=10, width=40)
buy_text.pack(expand=True, fill="both")
buy_text.tag_config("green", foreground="green")

# Coins to Ditch
ditch_frame = ttk.Frame(main_frame)
ditch_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

ditch_label = ttk.Label(ditch_frame, text="Coins to Ditch:")
ditch_label.pack(anchor="w")
ditch_text = tk.Text(ditch_frame, height=10, width=40)
ditch_text.pack(expand=True, fill="both")
ditch_text.tag_config("red", foreground="red")

update_data()
root.mainloop()

