# @madakixo 24032025-11:52
"""
ARIMA models require tuning of three parameters: p (autoregressive terms), d (differencing), and q (moving average terms)
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from itertools import product

# Load data
df = pd.read_csv('1960_onwards1.csv')

# Print column names for verification
print("Available columns in the CSV:", df.columns.tolist())

# Set date column and target variable
date_col = 'Year'
target_col = 'GDP growth (annual %)'

# Convert 'Year' to datetime and set as index
df[date_col] = pd.to_datetime(df[date_col], format='%Y')
df.set_index(date_col, inplace=True)

# Select the target series for forecasting
series = df[target_col]

# Check for stationarity using Augmented Dickey-Fuller test
def test_stationarity(timeseries):
    result = adfuller(timeseries, autolag='AIC')
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))

print("Stationarity test for original series:")
test_stationarity(series)

# Apply first-order differencing if not stationary
series_diff = series.diff().dropna()
print("\nStationarity test after first differencing:")
test_stationarity(series_diff)

# Grid search for ARIMA parameters
p = d = q = range(0, 3)
pdq = list(product(p, d, q))

best_aic = np.inf
best_param = None

for param in pdq:
    try:
        mod = ARIMA(series, order=param)
        results = mod.fit()
        if results.aic < best_aic:
            best_aic = results.aic
            best_param = param
        print('ARIMA{} - AIC:{}'.format(param, results.aic))
    except Exception as e:
        print(f"ARIMA{param} failed: {e}")
        continue

print(f'\nBest ARIMA{best_param} - AIC:{best_aic}')

# Fit the best model
best_model = ARIMA(series, order=best_param).fit()

# Forecast 30 years ahead (since data is yearly)
forecast = best_model.forecast(steps=30)
print("\nForecast for next 30 years (GDP growth %):")
print(forecast)# @madakixo 14012025-11:52
"""
ARIMA models require tuning of three parameters: p (autoregressive terms), d (differencing), and q (moving average terms)
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from itertools import product

# Load data
df = pd.read_csv('1960_onwards1.csv')

# Print column names for verification
print("Available columns in the CSV:", df.columns.tolist())

# Set date column and target variable
date_col = 'Year'
target_col = 'GDP growth (annual %)'

# Convert 'Year' to datetime and set as index
df[date_col] = pd.to_datetime(df[date_col], format='%Y')
df.set_index(date_col, inplace=True)

# Select the target series for forecasting
series = df[target_col]

# Check for stationarity using Augmented Dickey-Fuller test
def test_stationarity(timeseries):
    result = adfuller(timeseries, autolag='AIC')
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))

print("Stationarity test for original series:")
test_stationarity(series)

# Apply first-order differencing if not stationary
series_diff = series.diff().dropna()
print("\nStationarity test after first differencing:")
test_stationarity(series_diff)

# Grid search for ARIMA parameters
p = d = q = range(0, 3)
pdq = list(product(p, d, q))

best_aic = np.inf
best_param = None

for param in pdq:
    try:
        mod = ARIMA(series, order=param)
        results = mod.fit()
        if results.aic < best_aic:
            best_aic = results.aic
            best_param = param
        print('ARIMA{} - AIC:{}'.format(param, results.aic))
    except Exception as e:
        print(f"ARIMA{param} failed: {e}")
        continue

print(f'\nBest ARIMA{best_param} - AIC:{best_aic}')

# Fit the best model
best_model = ARIMA(series, order=best_param).fit()

# Forecast 30 years ahead (since data is yearly)
forecast = best_model.forecast(steps=30)
print("\nForecast for next 30 years (GDP growth %):")
print(forecast)
