from __future__ import print_function # for print(end="\r") 
from periphery import SPI # for SPI functions
# import sys # For sys ouput function
# import time # for delays

spi = SPI("/dev/spidev1.0",3,5000000)

# Address 0x31 OR'd with 0x40 MB bit
# Set 0x02: 8g range
setDataFormat = [0x71,0x02]

# Address 0x2D OR'd with 0x40 MB bit
# Set to 0x08: Measurement mode.
setPowerCtl = [0x6D,0x08]

# This the DATAX0 register (0x32) OR'd with Read bit (0x80)
# and Multiple Bytes bit (0x40). It is followed by 6 0x00 values
# to read 6 bytes starting from DATAX0. When transferred, this 
# returns 7 bytes: NULL (0x00), DATAX0 (0x32), DATAX1 (0x33), 
# DATAY0 (0x34), DATAY1 (0x35), DATAZ0 (0x36), and DATAZ1 (0x37).
dataX0 = [0xF2,0x00,0x00,0x00,0x00,0x00,0x00]

print ("\n Setting Data Format... \n")
spi.transfer(setDataFormat)

print ("\n Setting Power Control... \n")
spi.transfer(setPowerCtl)

# Takes LSB and MSB from any given axis
# and converts them into an integer
# from -256 to 255
def calcValue (lsb, msb):
    if msb == 255:
        trueValue = -256 + lsb
    else:
        trueValue = lsb
    return trueValue

# This loop constantly outputs the values read from the sensor.
# Ctrl-C to break.
print (" Accelerometer values:")
while True:
    value = spi.transfer(dataX0)
    trueX = calcValue(value[1],value[2])
    trueY = calcValue(value[3],value[4])
    trueZ = calcValue(value[5],value[6])
    print ("X:\t" + str(trueX).zfill(4) + "\tY:\t" + str(trueY).zfill(4) + "\tZ:\t" + str(trueZ).zfill(4), end="\r")