import RPi.GPIO as GPIO
import time


#GPIO setup

channel = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)
	
def TRX_off(pin):
	GPIO.output(pin, GPIO.LOW)  # Turn off the TRX
	print('Turn off')
	
#rrr

if __name__ == '__main__':
	try:
		TRX_off(channel)
		GPIO.cleanup()
	except KeyboardInterrupt:
		GPIO.cleanup()
		pass
