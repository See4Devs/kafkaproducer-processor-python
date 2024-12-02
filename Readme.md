# README

This project includes two components: a **processor** and a **producer**. The processor consumes messages from a Kafka topic (`iot-stream`), classifies sensor data (temperature and humidity), and writes the results to AWS Timestream. The producer generates 200 random sensor readings and publishes them to a NATS server.

## Prerequisites

1. **Python 3.7+** installed.
2. Install required libraries:
   ```bash
   pip install kafka-python boto3 nats-py
   ```
3. Ensure:
   - A Kafka server is running and accessible.
   - A NATS server is running locally at `nats://localhost:4222`.
   - AWS credentials and Timestream database/table are configured.

## How to Run

1. **Start the Processor**:

   - Run the script:
     ```bash
     python processor.py
     ```

2. **Run the Producer**:
   - Run the script:
     ```bash
     python producer.py
     ```

Ensure the processor is running before starting the producer.

## Workflow

1. The producer sends sensor readings to the NATS server.
2. The processor consumes the data from Kafka, processes it, and writes classified results to AWS Timestream.

## Notes

- Modify device IDs or data ranges in the producer to simulate different scenarios.
- Check logs for both scripts to ensure proper operation.

## Author

Lucien Chemaly
