"""
Set up Kafka with topics gdp_input, gdp_forecast, and gdp_errors.
Stream data into gdp_input (e.g., via a producer script or external source).
The pipeline buffers data and starts forecasting GDP once it has 10 points, sending results to gdp_forecast.
"""


from kafka import KafkaConsumer, KafkaProducer
import json
import time
from functools import wraps
import pandas as pd
from fbprophet import Prophet

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
INPUT_TOPIC = 'gdp_input'
OUTPUT_TOPIC = 'gdp_forecast'
ERROR_TOPIC = 'gdp_errors'

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, 
                         value_serializer=lambda m: json.dumps(m).encode('utf-8'))

# Buffer to store time series data
data_buffer = []

def backoff_retry(max_retries=3, initial_delay=1, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = initial_delay * (backoff_factor ** attempt)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s.")
                    time.sleep(delay)
        return wrapper
    return decorator

@backoff_retry()
def process_message(message):
    # Parse incoming message
    data = json.loads(message.value.decode('utf-8'))
    year = data['Year']
    gdp = data['GDP (current LCU)']
    
    # Add to buffer
    data_buffer.append({'ds': str(year), 'y': gdp})
    
    # Forecast when we have enough data (e.g., 10 years)
    if len(data_buffer) >= 10:
        df = pd.DataFrame(data_buffer)
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Simple Prophet forecast
        model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        model.fit(df)
        future = model.make_future_dataframe(periods=1, freq='Y')
        forecast = model.predict(future)
        
        # Return last forecast value
        return {'Year': future['ds'].iloc[-1].year, 'GDP_forecast': forecast['yhat'].iloc[-1]}
    return {'status': 'buffering', 'buffer_size': len(data_buffer)}

def error_handler(error, message):
    error_log = {
        'original_message': json.loads(message.value.decode('utf-8')),
        'error': str(error),
        'timestamp': time.time()
    }
    producer.send(ERROR_TOPIC, error_log)
    print(f"Error logged to {ERROR_TOPIC}: {error}")

def main_pipeline():
    consumer = KafkaConsumer(INPUT_TOPIC, 
                            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                            auto_offset_reset='earliest',
                            enable_auto_commit=True)

    for message in consumer:
        try:
            processed = process_message(message)
            producer.send(OUTPUT_TOPIC, processed)
            print(f"Processed message: {processed}")
        except Exception as e:
            error_handler(e, message)

if __name__ == '__main__':
    try:
        main_pipeline()
    except KeyboardInterrupt:
        print("Pipeline shutting down")
    finally:
        producer.flush()
