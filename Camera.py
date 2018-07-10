from RPi import GPIO
import threading
import os, io, base64, time, socket, picamera, daemon
import daemon.runner

class Capture:
    """ this class handles the licks
    """
    def __init__(self):
        self.path = '/home/pi/Pictures/'
        # setup GPIO
        #GPIO.cleanup()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup([20, 21], GPIO.OUT, initial=GPIO.LOW)
        GPIO.add_event_detect(26, GPIO.RISING, callback=self.shutter, bouncetime=1000)

        # setup camera
        self.camera_init()

        # ready indicator
        self.turn_on(20)
        self.turn_off(21)

    def camera_init(self):
        #self.camera = picamera.PiCamera(resolution=(640, 480), framerate=30)
        self.camera = picamera.PiCamera(resolution=(640, 480))
        self.camera.image_effect = 'none'
        self.camera.exposure_mode = 'sports'

    def shutter(self, foo):
        #start = time.time()
        self.turn_off(20)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.turn_on(21)
        self.camera.capture(os.path.join(self.path, timestr + '.jpg'), 'jpeg', use_video_port=False)
        #finish = time.time() - start
        #print(finish)
        self.turn_off(21)
        self.camera_cleanup()
        self.camera_init()
        self.turn_on(20)

    def turn_on(self, channel):
        GPIO.output(channel, GPIO.HIGH)

    def turn_off(self, channel):
        GPIO.output(channel, GPIO.LOW)

    def camera_cleanup(self):
        camThread = threading.Thread()
        while camThread.is_alive():
            camThread.join(1)
        camThread.run()
        self.camera.close()  # Gracefully close PiCam if client disconnects

    def cleanup(self):
        GPIO.remove_event_detect(26)
        GPIO.cleanup()
