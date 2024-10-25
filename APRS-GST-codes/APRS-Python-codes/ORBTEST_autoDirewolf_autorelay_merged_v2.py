#This code is for the automatic process of Turn on/ off Direwolf, and Turn on/ off Transceiver by the electronics relay based on the output El angle of the satellite orbit prediction 

import datetime
import time
import RPi.GPIO as GPIO
import subprocess
import os
import threading
from astropy.time import Time
from astropy.coordinates import EarthLocation
from astropy import units as u
from pycraf import satellite

# GPIO setup
channel = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

def TRX_on(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn on the TRX
    #print('Turn on')

def TRX_off(pin):
    GPIO.output(pin, GPIO.LOW)  # Turn off the TRX
    print('Turn off')

def extract_elevation_angle(line):
    # Split the line by ':' and extract the part containing the elevation angle
    elevation_part = line.split(':')[-1].strip()
    # Remove the unit 'deg' and convert the elevation angle to a float
    elevation_angle = float(elevation_part.split(' ')[0])
    return elevation_angle

def write_to_log(log_file_path, message):
    with open(log_file_path, 'a') as log_file:
        log_line = f"{datetime.datetime.utcnow()}: {message}\n"
        log_file.write(log_line)

def write_elevation_to_log(elevation_log_file_path, elevation_angle):
    with open(elevation_log_file_path, 'a') as elevation_log_file:
        elevation_log_file.write(f"{elevation_angle}\n")

def start_direwolf_and_kiss():
    # Kill existing Direwolf and KISS protocol processes
    subprocess.run(["pkill", "-f", "direwolf"])
    subprocess.run(["pkill", "-f", "kissutil"])

    direwolf_cmd = "x-terminal-emulator -e bash -c 'direwolf -p; exec bash'"
    subprocess.Popen(direwolf_cmd, shell=True)

    time.sleep(5)

    kissutil_cmd = "x-terminal-emulator -e bash -c 'kissutil -f /home/birdsx/test/msg; exec bash'"
    subprocess.Popen(kissutil_cmd, shell=True)

    time.sleep(10)

    output_dir = '/home/birdsx/test/msg'
    with open('/home/birdsx/Desktop/APRS_WS/output_de.txt', 'r') as original_file:
        for i, line in enumerate(original_file):
            new_file_name = os.path.join(output_dir, f'new_file_{i+1}.txt')
            with open(new_file_name, 'w') as new_file:
                new_file.write(line.strip())
            time.sleep(10)

# tle_string = '''move 2
# 1 43780U 18099Y   24043.89529067  .00018998  00000+0  11535-2 0  9999
# 2 43780  97.5390 108.4785 0008662  55.2099 304.9945 15.10517305283984'''

# latitude = 35.6528
# longitude = 139.8394
# altitude = 366.

# tle_string = '''ISS
# 1 25544U 98067A   24187.19119403  .00014758  00000+0  26954-3 0  9993
# 2 25544  51.6370 226.1297 0010193  31.8036 328.3566 15.49587198461346'''

tle_string = '''CURTIS
1 59507U 98067WG  24189.59363044  .00089653  00000+0  85425-3 0  9991
2 59507  51.6291 209.1545 0009157  26.4914 333.6547 15.65994461 13674'''

latitude = 33.89252
longitude = 130.84026
altitude = 366.

location = EarthLocation.from_geodetic(longitude, latitude, altitude)
sat_obs = satellite.SatelliteObserver(location)

log_file_path = '/home/birdsx/Desktop/orbtest.log'
elevation_log_file_path = '/home/birdsx/Desktop/elevation_log.txt'

# Clear the file at the start
# with open(log_file_path, 'w') as file:
    # file.write('')

def calculate_elevation_continuously():
    try:
        while True:
            dt = datetime.datetime.utcnow()
            obstime = Time(dt)
            az, el, dist = sat_obs.azel_from_sat(tle_string, obstime)
            log_message = f"Elevation: {el}"
            write_to_log(log_file_path, log_message)
            print(log_message)
            
            elevation_angle = extract_elevation_angle(log_message)
            write_elevation_to_log(elevation_log_file_path, elevation_angle)
            
            time.sleep(10)

    except Exception as e:
        error_message = f"Error: {e}"
        write_to_log(log_file_path, error_message)
        print(error_message)

# Start the elevation calculation thread
elevation_thread = threading.Thread(target=calculate_elevation_continuously)
elevation_thread.start()

direwolf_kiss_started = False

try:
    while True:
        time.sleep(10)
        # Check if elevation is -10 degrees or higher
        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()
            if lines:
                last_line = lines[-1]
                elevation_angle = extract_elevation_angle(last_line)
                if elevation_angle >= -5:
                    TRX_on(channel)
                if elevation_angle >= 3 and not direwolf_kiss_started:
                    start_direwolf_and_kiss()
                    direwolf_kiss_started = True
                    #break
                elif elevation_angle < -5:
                    #after completing transmission, wait 5 seconds before closing Kissutil and Direwolf 
                    #time.sleep(5)
                    subprocess.run(["pkill", "-f", "kissutil"])
                    subprocess.run(["pkill", "-f", "direwolf"])
                    direwolf_kiss_started = False
                    time.sleep(20)
                    TRX_off(channel)

finally:
    GPIO.cleanup()
