#updated phrophet and arima model

#

from kafka import KafkaConsumer, KafkaProducer
import json
import time
from functools import wraps

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
INPUT_TOPIC = 'input_topic'
OUTPUT_TOPIC = 'output_topic'
ERROR_TOPIC = 'error_topic'

# Kafka producer for sending processed messages and errors
producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, 
                         value_serializer=lambda m: json.dumps(m).encode('utf-8'))

def backoff_retry(max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Decorator for implementing retry logic with exponential backoff.
    """
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
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds.")
                    time.sleep(delay)
        return wrapper
    return decorator

@backoff_retry()
def process_message(message):
    """Process a single message."""
    # Simulating some processing logic
    data = json.loads(message.value.decode('utf-8'))
    processed_data = {'processed': data['data'] * 2}  # Example transformation
    return processed_data

def error_handler(error, message):
    """Handle errors by sending to an error topic."""
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
