from pynmeagps import NMEAReader
from serial import Serial
from time import sleep
from time import time
from sys import exit
import os
from datetime import datetime
import paho.mqtt.client as mqtt
import math
import random

serial_path = '/dev/ttyACM0'

if os.path.exists(serial_path):
    stream = Serial(serial_path, 9600)
    nmr = NMEAReader(stream)
else:
    stream = None
    nmr = None

MQTTURL = "9b7b323ee67e46d18f9317162c8e8841.s1.eu.hivemq.cloud"
MQTTUSERNAME = "sergiu.doncila"
MQTTPASSWORD = "QWEasd!@#123"
MQTTPORT = 8883
mqttClient = mqtt.Client()
mqttClient.tls_set()
mqttClient.username_pw_set(MQTTUSERNAME, MQTTPASSWORD)
mqttClient.connect(MQTTURL, MQTTPORT, 60)


def send_mqtt_message(topic, message):
    mqttClient.publish(topic, message)

def inc(m, item):
    if item.msgID in m:
        m[item.msgID] += 1
    else:
        m[item.msgID] = 1

m = {}

def readMessageFromRTK():
    if nmr == None:
        return None
    read = nmr.read()
    obj = NMEAReader.parse(read[0])
    return obj

def f(n):
    for i in range(n):
        obj = readMessageFromRTK()
        inc(m, obj)
    return

RADIUS = 3

def generate_random_point(origin):
    # Convert latitude and longitude from degrees to radians.
    lat, lon = math.radians(origin[0]), math.radians(origin[1])

    # Random angle.
    alpha = 2 * math.pi * random.random()
    # Random radius.
    r = RADIUS * math.sqrt(random.random())

    # Calculating the new coordinates.
    new_lat = lat + (r / 6378137) * (180 / math.pi)
    new_lon = lon + (r / 6378137) * (180 / math.pi) / math.cos(lat)
    return math.degrees(new_lat), math.degrees(new_lon)

def calculate_speed_and_vector(pos1, pos2, time_elapsed):
    # Calculate the distance.
    distance = calculate_distance(pos1, pos2)
    print(f"Inner d = {distance} ; time_elapsed = {time_elapsed}")

    # Speed = Distance / Time
    speed = distance / time_elapsed if time_elapsed > 0 else 0

    # Calculate the bearing between the two coordinates (movement vector).
    y = math.sin(math.radians(pos2[1]) - math.radians(pos1[1])) * math.cos(math.radians(pos2[0]))
    x = math.cos(math.radians(pos1[0])) * math.sin(math.radians(pos2[0])) - \
        math.sin(math.radians(pos1[0])) * math.cos(math.radians(pos2[0])) * \
        math.cos(math.radians(pos2[1]) - math.radians(pos1[1]))

    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360

    return speed, bearing

def calculate_target_vector(current_pos, fpoint):
    # Similar calculation to the one in calculate_speed_and_vector function.
    y = math.sin(math.radians(fpoint[1]) - math.radians(current_pos[1])) * math.cos(math.radians(fpoint[0]))
    x = math.cos(math.radians(current_pos[0])) * math.sin(math.radians(fpoint[0])) - \
        math.sin(math.radians(current_pos[0])) * math.cos(math.radians(fpoint[0])) * \
        math.cos(math.radians(fpoint[1]) - math.radians(current_pos[1]))

    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360

    return bearing

def calculate_required_rotation(svec, tvec):
    # Calculate the difference between the two vectors.
    angle = (tvec - svec + 360) % 360

    # If the angle is more than 180 degrees, it's shorter to rotate in the opposite direction.
    if angle > 180:
        angle -= 360

    return angle

def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formula used to calculate the bearing between two points is based on spherical trigonometry.
    :param pointA: tuple with (latitude, longitude) in degrees of the starting point
    :param pointB: tuple with (latitude, longitude) in degrees of the target point
    :returns: initial compass bearing in degrees from point A to point B, in the range [0,360)
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2() returns values
    # from -π to +π, which is not what we want for a compass bearing.
    # We need to normalize the result to a compass bearing range of [0,360).
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def calculate_distance(pointA, pointB):
    # Radius of the Earth in meters
    R = 6_371_000

    # Coordinates in radians
    lat1 = math.radians(pointA[0])
    lon1 = math.radians(pointA[1])
    lat2 = math.radians(pointB[0])
    lon2 = math.radians(pointB[1])

    # Differences in the coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula: a is the square of half the chord length between the points
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

    # c is the angular distance in radians
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c
    return distance*100


def get_current_position():
    obj = readMessageFromRTK()
    if obj == None:
        return (0,0)
    # while not(obj.msgID in ['GLL', 'RMC', 'GGA']):
    while not(obj.msgID in ['RMC']):
        obj = readMessageFromRTK()
    try:
        t = (float(obj.lat), float(obj.lon))
        return t
    except ValueError:
        return (0,0)


def stringy(p):
    return "(%.10f, %.10f)" % (p[0], p[1])

# base = (47.0634260983, 28.86726022)
# base = (47.0634493417, 28.8671470017)
# base = (47.0634170117, 28.8672567417)
base = (0.00000101, 0.0)
filename = "./a.out"
with open(filename, 'a') as file:
    while True:
        pos = get_current_position()
        d = calculate_distance(pos, base)
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        string = f"{currTime} Pos = {stringy(pos)} ;; D = {str(d)}"
        print(string)
        send_mqtt_message("microlab/automotive/device/atv/coordinates", stringy(pos))
        send_mqtt_message("microlab/automotive/device/atv/distance", str(d))
        file.write(string+"\n")
        sleep(60)

mqttClient.disconnect()
