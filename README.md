# Crypto-King
Simple crypto coin analysis tool
Crypto King

Crypto King is a comprehensive Python application for analyzing and monitoring cryptocurrency data. It leverages various tools and libraries to fetch cryptocurrency data from the CoinMarketCap API, perform data analysis, and present the results in a user-friendly GUI.
Features

    *Fetch Cryptocurrency Data: Retrieve the latest cryptocurrency data from CoinMarketCap using its API.
    *Data Analysis: Perform various financial analyses including percentage change, Relative Strength Index (RSI), Moving Averages, Bollinger Bands, and MACD.
    *Logging: Log activities and errors to a log file for debugging and monitoring purposes.
    *Graphical User Interface: Present the analyzed data in a user-friendly GUI with Tkinter.
    *Alerts: Provide alerts for coins to buy or ditch based on predefined conditions.

Requirements

    Python 3.7+
    requests
    json
    tkinter
    numpy
    scikit-learn
    logging
    os
----------------------------------------------------------------------------------------------------
-Installation-
Using a Batch File

To automate the installation of the required Python packages, you can use the following batch file:
----------------------------------------------------------------------------------------------------

-Setup-

Clone the repository:

git clone https://github.com/yourusername/crypto-king.git
cd crypto-king
-----------------------------------------------------------------------------------------------------

Run the script:

python crypto_king.py
-----------------------------------------------------------------------------------------------------
-Configuration-

Replace 'YOUR_API_KEY_HERE' in the script with your actual CoinMarketCap API key.

python

api_key = 'YOUR_API_KEY_HERE'

Logging

The script logs information to a file named crypto_analyzer.log on the user's desktop. This includes successful data fetches, errors, and analysis results.
Script Breakdown
Imports

The script uses the following Python libraries:

    -requests: For making HTTP requests to fetch data from the API.
    -json: For parsing JSON responses from the API.
    -tkinter: For creating the graphical user interface.
    -numpy: For numerical operations and calculations.
    -scikit-learn: For linear regression analysis.
    -logging: For logging information and errors.
    -os: For interacting with the operating system.

Fetching Data

The function fetch_crypto_data_and_save fetches cryptocurrency data from the CoinMarketCap API and saves it to a file. It logs the success or failure of this operation.
Reading Data

The function read_data_from_file reads the saved cryptocurrency data from a file and returns it as a Python dictionary.
Saving and Loading Previous Prices

Functions save_previous_prices and load_previous_prices handle saving and loading the previous prices of cryptocurrencies to and from a file.
Data Analysis

The script includes several functions for analyzing cryptocurrency data:

    calculate_percentage_change: Calculates the percentage change between current and previous prices.
    calculate_rsi: Calculates the Relative Strength Index.
    calculate_moving_average: Calculates the moving average.
    calculate_ema: Calculates the Exponential Moving Average.
    calculate_bollinger_bands: Calculates Bollinger Bands.
    calculate_macd: Calculates the Moving Average Convergence Divergence.

Data Display

The function display_data updates the GUI with the latest analysis results. It shows the top 5 increasing and decreasing cryptocurrencies, coins to buy, and coins to ditch.
GUI

The script creates a GUI using Tkinter, displaying the results of the analysis. It includes:

    Labels and text boxes for displaying the top 5 hot and sell coins.
    Text boxes for displaying coins to buy and ditch.
    Color-coded alerts for significant coins.

Periodic Updates

The function update_data fetches new data, analyzes it, and updates the GUI every minute.
Contribution

Feel free to fork the repository and submit pull requests. If you encounter any issues or have suggestions for new features, please open an issue.
