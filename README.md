Arduino board type: 'Arduino Uno'
Arduino version: '1.8.19'

Arduino board info: 
'''	
	BN: Arduino Uno
	VID: 2341
	PID: 0043
	SN: 55736303939351106231
'''



### Installation steps:

- Install Arduino firmware to our Ubuntu computer.
	sudo apt install arduino

- Give 'dialout' elevated permissions.
	sudo usermod -aG dialout blackjack

- Install PySerial: used to establish a serial connection and communicate with the Arduino from Python.
	pip install pyserial

- Install libcanberra-gtk-module.	
	sudo apt-get install libcanberra-gtk-module

	pip install dash redis



### Run this Arduino Code in the Arduino code editor

	// const int lightSensorPin = 345; // Replace A0 with the appropriate pin number you used to connect the OUT pin of the light sensor
	const int lightSensorPin = 5; // Replace with the appropriate digital pin number

	void setup() {
	Serial.begin(9600);
	}

	void loop() {
	int sensorValue = analogRead(lightSensorPin);
	Serial.println(sensorValue);
	delay(1000);
	}


### Run Kafka and ZooKeeper Containers in Docker

We used ```docker pull ubuntu/kafka:3.1-22.04_beta``` to download the Kafka Image specific to Ubuntu 22.04 from https://hub.docker.com/r/ubuntu/kafka Then we do a docker run to run the kafka container.

    docker run -d --name kafka-container -e TZ=UTC -p 9092:9092 -e ZOOKEEPER_HOST=host.docker.internal ubuntu/latest

If Kafka can't find ZooKeeper which it needs to run, you might need to expose the Kafka port to the host network. You can do this by adding the --network host option to the docker run command:

    docker run -d --name kafka-container --network host -e TZ=UTC -e KAFKA_ADVERTISED_HOST_NAME=host.docker.internal -v volume-Arduino:/Arduino_sensor_logger  -e KAFKA_ADVERTISED_PORT=9092 -e ZOOKEEPER_HOST=host.docker.internal ubuntu/kafka:latest

### Create Kafka topic called "Light-Sensor" 

Lets create a Kafka topic specifically to collect the logs from our light sensor connected to Arduino.

	kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 10 --topic Light-Sensor



