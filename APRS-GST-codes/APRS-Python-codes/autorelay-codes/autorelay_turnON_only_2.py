import RPi.GPIO as GPIO
import time

# GPIO setup
channel = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

def TRX_on(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn on the TRX
    print('Turn on')

def get_last_elevation(logfile_path):
    with open(logfile_path, 'r') as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-1]
            elevation_str = last_line.split('Elevation: ')[-1].split(' deg')[0]
            elevation = float(elevation_str)
            return elevation
    return None

# Path to the log file
logfile_path = '/home/birdsx/Desktop/orbtest.log'

elevation = get_last_elevation(logfile_path)
if elevation is not None:
    if elevation > -45:
        TRX_on(channel)
    else:
        print(f'Elevation is too low: {elevation} degrees')
else:
    print('Failed to read elevation from the log file')
