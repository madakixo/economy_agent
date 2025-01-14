# madakix0 

## prophet model for seasonality

from fbprophet import Prophet
import matplotlib.pyplot as plt

# Prepare data for Prophet which expects 'ds' for dates and 'y' for values
prophet_df = df.reset_index().rename(columns={'date_column': 'ds', 'feature1': 'y'})

# Initialize and fit the model
model = Prophet(
    yearly_seasonality=True,  # Add yearly seasonality if your data spans years
    weekly_seasonality=True,  # Weekly patterns
    daily_seasonality=True  # Daily patterns if data is at least daily frequency
)

# Add custom holidays if applicable
# model.add_country_holidays(country_name='US')

model.fit(prophet_df)

# Create future dataframe for predictions
future = model.make_future_dataframe(periods=30)  # forecast 30 days into future

# Predict
forecast = model.predict(future)

# Plotting the forecast
fig1 = model.plot(forecast)
plt.title('Prophet Forecast')

# Plot components of the forecast
fig2 = model.plot_components(forecast)
plt.show()

# If you want to look at specific parts of your forecast:
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
