# @madakixo 14012025-11:52
"""
ARIMA models require tuning of three parameters: p (autoregressive terms), d (differencing), and q 
"""
## agent for csv manipulation

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from itertools import product

# Load data
df = pd.read_csv('your_data.csv')
df['date_column'] = pd.to_datetime(df['date_column'])
df.set_index('date_column', inplace=True)

# Assume we're forecasting 'feature1'
series = df['feature1']

# Check for stationarity using Augmented Dickey-Fuller test
def test_stationarity(timeseries):
    result = adfuller(timeseries, autolag='AIC')
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))

test_stationarity(series)

# If not stationary, apply differencing until it is
# Here's an example of first-order differencing:
series_diff = series.diff().dropna()
test_stationarity(series_diff)

# Now, we'll perform a grid search for ARIMA parameters
p = d = q = range(0, 3)
pdq = list(product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(product(p, d, q))]

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
    except:
        continue

print('Best ARIMA{} - AIC:{}'.format(best_param, best_aic))

# Fit the best model
best_model = ARIMA(series, order=best_param).fit()

# Forecast
forecast = best_model.forecast(steps=30)  # 30 steps ahead
print(forecast)
