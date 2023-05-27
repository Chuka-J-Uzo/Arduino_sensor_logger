from confluent_kafka import Producer
import json
import serial
import csv
import redis
from datetime import datetime

serial_port = '/dev/ttyACM0'  # Replace with the appropriate serial port on your computer
baud_rate = 9600

serial_connection = serial.Serial(serial_port, baud_rate)

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',
    'queue.buffering.max.messages': 2000000,
    'queue.buffering.max.kbytes': 3000000,
    'partitioner': 'consistent',
    'message.send.max.retries': '5',
    'request.required.acks': '-1',
    'compression.type': 'lz4',
    'compression.level': '6'
})

redis_host = "172.17.0.3"
redis_port = 6379
redis_db = redis.Redis(host=redis_host, port=redis_port, db=0)
redis_key = "KAFKA_DB2:light_sensor_data"

csv_file = open('sensor_data.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)

while True:
    if serial_connection.in_waiting > 0:
        sensor_value = serial_connection.readline().strip().decode('utf-8')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp
        csv_writer.writerow([timestamp, sensor_value])
        print("Timestamp:", timestamp, "Sensor Value:", sensor_value)

        # Create a JSON payload with the timestamp and sensor value
        payload = json.dumps({'timestamp': timestamp, 'sensor_value': sensor_value}).encode('utf-8')

        # Send the payload to the Kafka topic
        producer.produce('Light-Sensor', value=payload)

        # Store the sensor value in Redis
        redis_db.rpush(redis_key, sensor_value)

        # Flush the producer to ensure the message is sent
        producer.flush()

csv_file.close()
serial_connection.close()
