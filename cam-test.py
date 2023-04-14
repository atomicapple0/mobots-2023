from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = [1024, 768]
camera.start_preview()

sleep(2)

filename = 'cvcar/imgs/misc/yay.jpg'
camera.capture(filename)

print(f"saved {filename}")

camera.close()