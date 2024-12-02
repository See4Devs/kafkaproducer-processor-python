import random
import asyncio
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    try:
        print("Connecting to NATS server...")
        await nc.connect("nats://localhost:4222")
        print("Connected to NATS server.")

        device_id = "device-001"  # Static device ID

        for i in range(200):
            data = {
                "device_id": device_id,
                "temperature": round(random.uniform(20.0, 30.0), 2),  # Random temperature between 20.0 and 30.0
                "humidity": round(random.uniform(40.0, 70.0), 2)       # Random humidity between 40.0 and 70.0
            }
            await nc.publish("sensor_data", str(data).encode())
            print(f"Published message {i + 1}: {data}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing connection...")
        await nc.close()
        print("Connection closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to run the main function: {e}")
