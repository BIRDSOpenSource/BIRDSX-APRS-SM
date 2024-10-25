import RPi.GPIO as GPIO
import time


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
	
#rrr

if __name__ == '__main__':
	try:
		TRX_on(channel)
		time.sleep(30)
		TRX_off(channel)
		time.sleep(10)
		GPIO.cleanup()
	except KeyboardInterrupt:
		GPIO.cleanup()
		pass
