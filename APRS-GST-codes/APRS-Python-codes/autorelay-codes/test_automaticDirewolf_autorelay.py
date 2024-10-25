import subprocess
import os
import time
import RPi.GPIO as GPIO


#GPIO setup

channel = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

def TRX_on(pin):
	GPIO.output(pin, GPIO.HIGH)  # Turn on the TRX
	print('Turn on')
	
def TRX_off(pin):
	GPIO.output(pin, GPIO.LOW)  # Turn off the TRX
	print('Turn off')

# Define the Direwolf commands
direwolf_cmd = "direwolf -p"
kissutil_cmd = "kissutil -f /home/birdsx/test/msg"

TRX_on(channel)

# Opening direwolf
print("Executing direwolf...")
subprocess.Popen(direwolf_cmd.split())

# Wait for 5 seconds before opening kissutil
time.sleep(5)

# Execute kissutil command
print("Executing kissutil...")
subprocess.Popen(kissutil_cmd.split())

print("Commands executed successfully.")

# Wait for 10 seconds before the first transmission
time.sleep(10)

# Access directory path for the APRS data files
output_dir = '/home/birdsx/test/msg'

# Open the original file and read line by line
with open('/home/birdsx/Desktop/APRS_WS/output_de.txt', 'r') as original_file:
    for i, line in enumerate(original_file):
        # Construct the file name for the new file
        new_file_name = os.path.join(output_dir, f'new_file_{i+1}.txt')
        # Write the current line to a new file
        with open(new_file_name, 'w') as new_file:
            new_file.write(line.strip())
        
        print(f"File {new_file_name} created.")
        
        # Pause for xxx seconds
        time.sleep(10)

#print("Files created successfully.")

# Wait for 20 seconds before closing Direwolf
time.sleep(20)

#Closing YAESU TRX
TRX_off(channel)
GPIO.cleanup()
