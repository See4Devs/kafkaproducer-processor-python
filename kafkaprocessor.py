from kafka import KafkaConsumer
import boto3
import json
import time

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    'iot-stream',
    bootstrap_servers="YOUR-BOOTSTRAP-SERVER-URL",
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username="YOUR-REDPANDA-USERNAME",
    sasl_plain_password="YOUR-REDPANDA-PASSWORD",
    ssl_check_hostname=True,
    ssl_cafile=None
)

# AWS Timestream Configuration
timestream = boto3.client('timestream-write', region_name="YOUR-AWS-REGION", aws_access_key_id="YOUR-AWS-KEY-ID", aws_secret_access_key="YOUR-AWS-ACESS-KEY")

# Define the Timestream database and table
DATABASE_NAME = "iot_data"
TABLE_NAME = "sensor_metrics"

# Function to classify temperature and humidity levels
def classify_environment(temperature, humidity):
    temperature = float(temperature)
    humidity = float(humidity)
    if temperature > 35 or humidity > 70:
        return "Dangerous"
    elif 25 <= temperature <= 35 and 40 <= humidity <= 70:
        return "Optimal"
    else:
        return "Warning"

# Function to write data to Timestream
def write_to_timestream(message):
    max_retries = 3
    retry_interval = 1  # in seconds

    try:
        payload = json.loads(message.value)
        print(f"Processing payload: {payload}")

        # Extract temperature and humidity, use defaults if missing
        temperature = str(payload.get("temperature", "0"))
        humidity = str(payload.get("humidity", "0"))
        environment_status = classify_environment(temperature, humidity)
        print(environment_status, "environment_status")
        # Prepare dimensions from the payload, excluding timestamp, temperature, and humidity
        dimensions = [
            {"Name": key, "Value": str(value)}
            for key, value in payload.items()
            if key not in ["timestamp", "temperature", "humidity"]
        ]

        # Add additional dimensions for tracking and classification
        dimensions.append({"Name": "processed_by", "Value": "KafkaProcessor"})
        dimensions.append({"Name": "environment_status", "Value": environment_status})

        # Current timestamp in milliseconds
        current_time_millis = str(int(time.time() * 1000))

        # Construct records with dynamic MeasureName
        records = [
            {
                "Dimensions": dimensions,
                "MeasureName": "environment",
                "MeasureValueType": "MULTI",
                "MeasureValues": [
                    {
                        "Name": "temperature",
                        "Value": str(temperature),
                        "Type": "DOUBLE"
                    },
                    {
                        "Name": "humidity",
                        "Value": str(humidity),
                        "Type": "DOUBLE"
                    },
                    {
                        "Name": "status",
                        "Value": str(environment_status),
                        "Type": "VARCHAR"
                    }
                ],
                "Time": current_time_millis
            }
        ]

        # Retry logic for Timestream write
        for attempt in range(max_retries):
            try:
                response = timestream.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME, Records=records)
                print(f"Successfully wrote to Timestream: {response}")
                break
            except timestream.exceptions.RejectedRecordsException as e:
                print(f"Write attempt {attempt + 1} failed due to rejected records: {e}")
                time.sleep(retry_interval * (2 ** attempt))  # Exponential backoff
            except Exception as e:
                print(f"Write attempt {attempt + 1} failed: {e}")
                time.sleep(retry_interval * (2 ** attempt))
        else:
            print(f"Failed to write to Timestream after {max_retries} attempts.")

    except json.JSONDecodeError:
        print(f"Invalid JSON message: {message.value}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main loop: Consume messages from Kafka
for message in consumer:
    print(f"Received message: {message.value}")
    write_to_timestream(message)
