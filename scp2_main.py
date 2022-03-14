'''
Code for SCP V2. Testing Arducam motor camera + Neo Pixel + Pi zero in space environment 
Using UART serial communication with the following setup:

Baud rate: 115200
Parity: No
Stopbits: 1
Bytes order: Big endian

The system supports the following three commands:

1. 
Name: Take image
Description: Takes an image from the Arducam camera and returns the image size in bytes
OP code: 0x00
Parameters: 
    Focus: 1 byte value from 0-104 (the actual focus value will be multiple by 10) 
    Red: 1 byte value for the Led's Red value
    Green: 1 byte value for the Led's Green value
    Blue: 1 byte value for the Led's Blue value 
Returns:
    image size: 3 bytes   


2. 
Name: Get image
Description: Get the data of the last taken image. Call Take image first!
OP code: 0x01
Parameters:
    None
Returns:
    The last image data. The number of bytes is what the last "take image" oprtaion returned   


3. 
Name: Get telemetry
Description: Gets telemetry data from the PI. CPU temparture,CPU load 
OP code: 0x02
Parameters:
    None
Returns:
    CPU Temparture: 1 byte
    CPU Load: 1 byte

'''

import time
import serial
import os
import board
import neopixel
from datetime import datetime
import logging
import threading
from ctypes import *
import traceback
from gpiozero import CPUTemperature
from gpiozero import LoadAverage

ser = serial.Serial ("/dev/ttyS0", 115200,parity='N',stopbits=1, timeout=0.1)    #on PI4
pixels = neopixel.NeoPixel(board.D21, 5,brightness =1)
IMAGE_FILE_NAME ="/home/pi/dev/scp2/image.jpg"


# takes a picture from Arducam camera
def take_pic(f ,r, g, b):
    print("About to take an image. Focus:%d,Red:%d,Green:%d,Blue:%d" %(f,r,g,b))
    pixels.fill((r, g, b))
    pixels.show()

    cmd = "raspistill -w 640 -h 480 -n -t 100 -q 20 -e jpg -th none -o %s" %IMAGE_FILE_NAME
    # cmd = "raspistill -q 30 -o %s" %saved_file_name
    print(cmd)
    os.system(cmd)
    pixels.fill((0, 0 , 0))
    with open(IMAGE_FILE_NAME, "rb") as image:
        file = image.read()
        size = len(file)
    return size

# get last image data
def get_image():
    with open(IMAGE_FILE_NAME, "rb") as image:
        file = image.read()
        size = len(file)
        print(size)
        for i in range (size):
            ser.write(bytes([file[i]]))
        print("image sent...")

# get telemetry data
def get_telemetry():
    cpu_temp = CPUTemperature()
    cpu_temp = int(cpu_temp.temperature)
    cpu_load = int(LoadAverage(minutes=1).load_average*100)
    in_bytes = cpu_temp.to_bytes(1,'big')
    ser.write(in_bytes)
    in_bytes = cpu_load.to_bytes(1,'big')
    ser.write(in_bytes)
    print("Sent telemetry. CPU temp: %d, cpu load: %d" % (cpu_temp,cpu_load))

# main loop
def main():
    print("start")
    while True:
        try:
            received_data = ser.read(1)              
            print(received_data)
            if received_data == b'\x00':
                print(received_data, "take image")
                f = ser.read(1)
                f = int.from_bytes(f, "big")
                r = ser.read(1)
                r = int.from_bytes(r, "big")
                g = ser.read(1)
                g = int.from_bytes(g, "big")
                b = ser.read(1)
                b = int.from_bytes(b, "big")
                # take an image ...
                size = take_pic(f, r, g, b)
                # return the size of the image ...
                in_bytes = size.to_bytes(3,'big')
                ser.write(in_bytes)
            elif received_data == b'\x01':
                print(received_data, "get image")
                get_image()
            elif received_data == b'\x02':
                print(received_data, "get telematry")
                get_telemetry()
            # else:
            #     print("no data")
            time.sleep(1)
        except Exception:
            print(traceback.format_exc())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
