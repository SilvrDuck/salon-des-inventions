import sys
import time

import machine
import ubinascii
from machine import Pin
from umqtt import MQTTClient, MQTTException

SERVER_IP = "192.168.1.69"

MAIN_TOPIC = b"LED_MAIN"
SECONDARY_TOPIC = b"LED_SECONDARY"
AMBIENT_TOPIC = b"LED_AMBIENT"

TOPICS = [MAIN_TOPIC, SECONDARY_TOPIC, AMBIENT_TOPIC]

mqtt_client = None

# ======================== I/O ========================
# region I/O

print("Setting up I/O...")

pins = {
    MAIN_TOPIC: {
        "red": Pin(0, Pin.OUT),
        "green": Pin(2, Pin.OUT),
        "blue": Pin(4, Pin.OUT),
    },
    SECONDARY_TOPIC: {
        "red": Pin(19, Pin.OUT),
        "green": Pin(21, Pin.OUT),
        "blue": Pin(22, Pin.OUT),
    },
    AMBIENT_TOPIC: {
        "red": Pin(5, Pin.OUT),
        "green": Pin(15, Pin.OUT),
        "blue": Pin(18, Pin.OUT),
    }
}

color_map = {
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "black": (0, 0, 0),
    "white": (1, 1, 1),
    "purple": (1, 0, 1),
    "yellow": (1, 1, 0),
    "cyan": (0, 1, 1),
}

def set_rgb(r, g, b, target):
    if target == AMBIENT_TOPIC:
        if g > 0:
            print("Warning: Ambient green light is broken, setting to black instead.")
            r, g, b = 0, 0, 0

    pins[target]["red"].value(r)
    pins[target]["green"].value(g)
    pins[target]["blue"].value(b)

def set_color(color, target):
    set_rgb(*color_map[color], target)

# ======================== MQTT ========================
# region MQTT

def setup_mqtt():
    print("Connecting to MQTT...")
    client = MQTTClient(
        ubinascii.hexlify(machine.unique_id()),
        SERVER_IP,
        keepalive= 12 * 60 * 60,
    )
    client.set_callback(receive_callback)
    try:
        client.connect(clean_session=False)
        print("Connected to MQTT broker!")
    except Exception as e:
        print("Failed to connect to MQTT server:")
        sys.print_exception(e)
        raise e
    for topic in TOPICS:
        client.subscribe(topic, qos=1)
    return client

def decode_message(message):
    message = message.decode("utf-8")

    color_times = message.split(";")

    timeseries = []
    for color_time in color_times:
        color, ms, transition = color_time.split("|")
        _ = transition  # Unused
        timeseries.append((color, int(ms)))

    return timeseries

def receive_callback(topic, msg):
    print("Received message on topic {}: {}".format(topic, msg))
    if topic not in pins:
        print("Unknown topic: {}".format(topic))
        return

    timeseries = decode_message(msg)
    state = timeseries_state[topic]
    state['timeseries'] = timeseries
    state['current_index'] = 0
    state['next_change_time'] = time.ticks_ms()

# ======================== Topic handling ========================
# region Topic handling

# Timeseries state for each topic
timeseries_state = {
    topic: {
        'timeseries': [],
        'current_index': 0,
        'next_change_time': 0,
    } for topic in TOPICS
}

def process_topic(topic, current_time):
    state = timeseries_state[topic]
    if state['timeseries']:
        if time.ticks_diff(current_time, state['next_change_time']) >= 0:
            color, ms = state['timeseries'][state['current_index']]
            print("Setting color {} on topic {} for {} ms".format(color, topic, ms))
            set_color(color, topic)
            state['current_index'] += 1
            if state['current_index'] >= len(state['timeseries']):
                # Loop back to the beginning of the timeseries
                state['current_index'] = 0
            # Schedule next change
            state['next_change_time'] = time.ticks_add(current_time, ms)

def update_leds(current_time):
    for topic in TOPICS:
        process_topic(topic, current_time)

# ======================== Main ========================
# region Main

def handle_mqtt_failure(failure_count):
    print("Warning: MQTT check failed, retry count: {}".format(failure_count))
    failure_count += 1
    return failure_count

def main():
    global mqtt_client
    failure_count = 0
    print("Main loop started.")

    mqtt_client = setup_mqtt()

    while True:
        try:
            mqtt_client.check_msg()
            current_time = time.ticks_ms()
            update_leds(current_time)
            failure_count = 0
            time.sleep_ms(10)
        except (OSError, MQTTException):
            failure_count = handle_mqtt_failure(failure_count)
            if failure_count > 5:
                # Attempt to reconnect
                print("Attempting to reconnect to MQTT server...")
                try:
                    mqtt_client.disconnect()
                except:  # noqa
                    pass  # Ignore disconnect errors
                mqtt_client = setup_mqtt()
                failure_count = 0  # Reset failure count after reconnection

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        print("Exception occurred in main loop:")
        sys.print_exception(e)

    finally:
        try:
            if mqtt_client is not None:
                mqtt_client.disconnect()
        except Exception as e:
            print("Failed to disconnect MQTT client:")
            sys.print_exception(e)
        finally:
            print("Resetting...")
            machine.reset()
