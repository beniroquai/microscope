import time
import serial
from microscope.lasers.esplaser import ESPLaser
#from microscope.cameras.atmcd import AndorAtmcd

'''setup serial connection first'''
# Very hacky to have always the same Serial device..
serialadress = '/dev/cu.SLAB_USBtoUART'
#serialadress = '/dev/ttyUSB0'
serialdevice = serial.Serial(serialadress, 115200, timeout=.1)
time.sleep(1)

# Initiliaze Laser connection
laser = ESPLaser(connection=serialdevice)
laser.enable()
laser._set_power_mw(30)
time.sleep(1)
laser._set_power_mw(3000)

'''
camera = AndorAtmcd(uid='9146')
camera.enable()
camera.set_exposure_time(0.15)

data = []
for i in range(10):
    data.append(camera.trigger_and_wait())
    print("Frame %d captured." % i)
print(data)
camera.disable()
'''
laser.disable()