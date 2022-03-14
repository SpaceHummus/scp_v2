'''
Sample usage code for using SCP V2. Testing Arducam motor camera + Neo Pixel + Pi zero in space environment 
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

ser = serial.Serial ("/dev/ttyS0", 115200,parity='N',stopbits=1, timeout=0.1)    #Serial settings for  PI4 / PI Zero. Note that on other types of PIs it might be diffrent 
IMAGE_FILE_NAME = "image.jpg" # output image name

# waits until data is ready in the serial buffer
# bytes_count - how many bytes should we read from serial buffer
# to_int - convert the bytes to int? True/False
def wait4result(bytes_count, to_int):
    data = ser.read(bytes_count)
    while data == b'':  # wait for the result to be ready      
        print("waiting for result...")
        time.sleep(0.1) 
        data = ser.read(bytes_count)
    if to_int:
        return int.from_bytes(data, "big")
    else:
        return data

def take_image(): 
    ser.write(b'\x00') # OP code 00 - take image
    ser.write(b'\xA0') # the focus 0-102 - will be multiply by 10
    ser.write(b'\xA1') # LED's Red value 0-255
    ser.write(b'\xA2') # LED's Green value 0-255
    ser.write(b'\x12') # LED's Blue value 0-255
    
    size = wait4result(3,True)
    print ("image size:",size)
    return size


def get_image(file_size): 
    print("getting the image, please wait...")
    ser.write(b'\x01') # OP code 00 - take image
    with open(IMAGE_FILE_NAME, "wb") as image:
        for i in range(file_size):
            s = wait4result(1,False)
            image.write(s)
            # print(s)
        print("Done getting the image")
    
def get_telemetry(): 
    ser.write(b'\x02')
    cpu_temp = wait4result(1,True)
    cpu_load = wait4result(1,True)
    print("Got telemetry. CPU temp: %d, cpu load: %d" % (cpu_temp,cpu_load))

if __name__ == "__main__":
    try:
        get_telemetry() # cpu load should be low 
        f_size = take_image()
        get_image(f_size)
        get_telemetry() # cpu load should be high due to image processing / TX
    finally:
        ser.close()   


