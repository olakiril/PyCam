from RPi import GPIO
import threading
import os, io, base64, time, socket, picamera, daemon
import daemon.runner

class Capture:
    """ this class handles the licks
    """
    def __init__(self):
        self.path = '~'
        # setup GPIO
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup([20, 21], GPIO.OUT, initial=GPIO.LOW)
        GPIO.add_event_detect(26, GPIO.RISING, callback=self.shutter, bouncetime=2000)

        # setup camera
        self.camera_init()

        # ready indicator
        self.turn_on(20)

    def camera_init(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        # camera.zoom = (0.2, 0.2, 1.0, 1.0)
        self.camera.exposure_mode = 'sports'
        print('Camera server running')

    def shutter(self, foo):
        if GPIO.input(26):
            self.turn_off(20)
            self.turn_on(21)
            start = time.time()
            print('Taking picture')
            self.camera.capture('picam-latest-snap.jpg')
            finish = time.time() - start
            print(finish)
            print('Picture Taken!')
            self.turn_off(21)
            self.camera_cleanup()
            self.camera_init()
            self.turn_on(20)

    def turn_on(self, channel):
        GPIO.output(channel, GPIO.HIGH)

    def turn_off(self, channel):
        GPIO.output(channel, GPIO.LOW)

    def camera_cleanup(self):
        print('Camera thread starting.')
        camThread = threading.Thread()
        while camThread.is_alive():
            camThread.join(1)
        camThread.run()
        print('Camera thread ended')
        self.camera.close()  # Gracefully close PiCam if client disconnects

    def cleanup(self):
        GPIO.remove_event_detect(26)
        GPIO.cleanup()
