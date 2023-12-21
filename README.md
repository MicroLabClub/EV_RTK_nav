### RTK Receiver

## How to use

Firstly you need to enable virtual environment
`source ./rtk_py_env/bin/activate`

And then you need to change ownership to your user
`sudo chown USER /dev/ttyACM0`

RTK is by default connected to `/dev/ttyACM0`

Now you can send the data to MQTT server with
`python main.py`

## Topics

microlab/automotive/device/atv/coordinates - for coordinates
microlab/automotive/device/atv/distance - for distance

## Dependencies

docopt      0.6.2
hbmqtt      0.9.6
paho-mqtt   1.6.1
passlib     1.7.4
pip         23.2.1
pynmeagps   1.0.32
pyserial    3.5
PyYAML      6.0.1
setuptools  65.5.0
six         1.16.0
transitions 0.9.0
websockets  12.0

