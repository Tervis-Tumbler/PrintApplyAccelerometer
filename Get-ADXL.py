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
        # - Clock frequency set to 400KHz
    spi = SPI("/dev/spidev1.0",3,400000)
    
    # Address 0x31 OR'd with 0x40 MB bit.
    # Set to 0x08: 16g Full (13-bit) Resolution - 4mg/LSB.
    setDataFormat = [0x71,0x0F]
    
    # Address 0x2D OR'd with 0x40 MB bit.
    # Set to 0x08: Measurement mode.
    setPowerCtl = [0x6D,0x08]
    
    # Address 0x2C OR'd with 0x40 MB bit.
    # Set to 0x0D: 800 Hz Output Data Rate    
    setDataRate = [0x6C,0x0D]
    
    # Transfer settings to ADXL345.
    spi.transfer(setDataFormat)
    spi.transfer(setPowerCtl)
    spi.transfer(setDataRate)
    
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

# Directory for JSON files
directory = "/media/card/"

# Time between samples.
sampleRate = .005

# Initialize SPI object.
spi = initiateADXL345()

# Initialize array.
data = []  

# Set up pin values and properties.
switchPin = GPIO1_28    # pin P9.12
ledPin = GPIO1_16       # pin P9.15
pinMode(ledPin, OUTPUT)
pinMode(switchPin, INPUT, PULLUP)

toggle = 1

# Main loop.
while True:
    
    # If switch is pressed, record data:
    if ((digitalRead(switchPin) == 0) & (toggle == 1)):
        
        # Turn on LED.
        digitalWrite(ledPin,HIGH)
        
        # Add to data array 
        data.extend(getData(spi))
        
        # Wait for sample rate.
        time.sleep(sampleRate)
        
    # Egress cycle
    elif ((digitalRead(switchPin) == 1) & (toggle == 1)):
        
        # Record start time.
        timeStart = time.time()
        
        # Open file object with name format "ADXL_timestamp.txt.
        file = open((directory + "ADXL_" + "%.0f" % (timeStart*100) + ".txt"),'wb')
        
        # Convert to string and format to one object per line.
        file.write(json.dumps(data) + "\n")

        # Close file.
        file.close()
        
        # Reset data array.
        data = []
        
        # Set toggle to 0.
        toggle = 0
        
        # Confirmation flash.
        digitalWrite(ledPin,LOW)
        time.sleep(0.3)
        digitalWrite(ledPin,HIGH)
        time.sleep(0.3)
        digitalWrite(ledPin,LOW)
        time.sleep(0.3)
        digitalWrite(ledPin,HIGH)
        time.sleep(0.3)
        digitalWrite(ledPin,LOW)

    
    # Reset toggle if 0 and button is pressed.
    elif ((digitalRead(switchPin) == 0) & (toggle == 0)):
        toggle = 1
    
    # Otherwise, if switch is not pressed, wait 1 second and check again.
    else:
        digitalWrite(ledPin,LOW)
        # print ("Waiting...")
        time.sleep(1)