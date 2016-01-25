#!/usr/bin/python

# Gets values from the ADXL345 and saves them to 
# /media/card, which is the directory for the uSD
# card attached to the BeagleBone Black.

from __future__ import print_function # for print(end="\r") 
from periphery import SPI # for SPI functions
import time # for timestamp and sleep functions.
import json # for converting data array to JSON.
from bbio import * # for BeagleBone Black pin functions.


# Initialize SPI communication with the ADXL345.
def initiateADXL345():
    
    # Creates SPI object with the following parameters:
        # - SPI device as "/dev/spidev1.0"
        # - Clock mode 3 (i.e., sets clock polarity 1, clock phase 1)
        # - Clock frequency set to 5 MHz
    spi = SPI("/dev/spidev1.0",3,5000000)
    
    # Address 0x31 OR'd with 0x40 MB bit.
    # Set to 0x08: Full Resolution - 4mg/LSB.
    setDataFormat = [0x71,0x0F]
    
    # Address 0x2D OR'd with 0x40 MB bit.
    # Set to 0x08: Measurement mode.
    setPowerCtl = [0x6D,0x08]
    
    # print ("\n Setting Data Format... \n")
    spi.transfer(setDataFormat)
    
    # print ("\n Setting Power Control... \n")
    spi.transfer(setPowerCtl)
    return spi


# Parse data from accelerometer.
def combineBytes (lsb, msb, bits, offset):
    
    # Shift MSB to the left.
    MSB = msb << 8
    
    # Combine MSB and LSB.
    combo = MSB | lsb
    
    # Remove trailing bits.
    combo = combo >> 3
    
    # Perform Two's Complement, with offset if needed.
    sign_bit = 1 << (bits - 1)
    return (combo & (sign_bit - 1)) - (combo & sign_bit) + offset


# Define value indices for a given axis.
def axisVariable(axis):
    if axis == 'x':
        j = 1
        k = 2
        return j,k
    elif axis == 'y':
        j = 3
        k = 4
        return j,k
    elif axis == 'z':
        j = 5
        k = 6
        return j,k
    else:
        print ("Invalid axis.")
        return


# Gets data from accelerometer. Returns array with values.
def getData(adxl):
    
    # Get values from accelerometer.
    value = adxl.transfer(dataX0)
    
    # Initialize array with timestamp.
    axisValues = [{"time":time.time()}]
    
    for a in ['x','y','z']:
        # Value index associated with axis measured.
        j,k = axisVariable(a)
        
        # Combine data and perform Two's Complement.
        combinedValue = combineBytes(value[j],value[k],13,6)
        
        # Add values to the array.
        iter(axisValues).next()[a] = combinedValue
    
    # Contains data array [{"time":timestamp,"x":xValue,"y":yValue,"z":zValue}]
    return axisValues
    

# This is the DATAX0 register (0x32) OR'd with Read bit (0x80)
# and Multiple Bytes bit (0x40). It is followed by 6 0x00 values
# to read 6 bytes starting from DATAX0. When transferred, this 
# returns 7 bytes: NULL (0x00), DATAX0 (0x32), DATAX1 (0x33), 
# DATAY0 (0x34), DATAY1 (0x35), DATAZ0 (0x36), and DATAZ1 (0x37).
dataX0 = [0xF2,0x00,0x00,0x00,0x00,0x00,0x00]

# Time between samples.
sampleRate = .010

# Number of samples to take before dumping to disk.
sampleSize = 50

# Initialize SPI object.
spi = initiateADXL345()

# Initialize array.
data = []  

# Initialize counter.
i = 0

print (" Accelerometer values:")
while True:
    data = getData(spi)
    print ("X:\t" + str(data[0]['x']).zfill(6) + "\tY:\t" + str(data[0]['y']).zfill(6) + "\tZ:\t" + str(data[0]['z']).zfill(6), end="\r")
    time.sleep(.01)