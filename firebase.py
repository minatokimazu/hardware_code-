#!/usr/bin/python
#
# Reference: Matt Hawkins's Code on
# http://www.raspberrypi-spy.co.uk/

# Revised by Minh Nguyen Dep trai
#--------------------------------------
import time
import board
import busio
import adafruit_veml7700
import SI1145.SI1145 as SI1145
from time import sleep
from adafruit_htu21d import HTU21D
import pyrebase

#This code has three I2C devices. The Python code here is to read from/write to the device 
# via these addresses. 
i2c1 = busio.I2C(board.SCL, board.SDA)
sensor_vem = adafruit_veml7700.VEML7700(i2c1)

i2c2 = busio.I2C(board.SCL, board.SDA)
sensor_htu = HTU21D(i2c2)

sensor_si1 = SI1145.SI1145()
#Initialize the Pi 
# Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0



# configuration of the database access
# Global objects: config and user
# ====================================================================================================
config = {
    "apiKey": "AIzaSyC8uOx7qIkvCh4kwAP05xb7-NISZyCjdyc",
    "authDomain": "fir-aeb23.firebaseapp.com",
    "databaseURL": "https://fir-aeb23.firebaseio.com/",
    "storageBucket": "gs://fir-aeb23.appspot.com",
}
user = None  # define user as a global variable to access from all the functions.
# ====================================================================================================

# The authorization function
# ====================================================================================================
def GetAuthorized(firebase):
    global user
    auth = firebase.auth()  # Get a reference to the auth service
    # authenticate a user
    try:
        user = auth.sign_in_with_email_and_password("nguyenminhnguyen2611@gmail.com",
                                                    "123456")  # username and password of your account for database
        print(user)  # display the user information, if successful
    except:
        print("Not authorized")
        user = None

# The function to initialize the database.
# ====================================================================================================
def dbInitialization():
    firebase = pyrebase.initialize_app(config)  # has to initialize the database
    GetAuthorized(firebase)  # get authorized to operate on the database.
    return firebase

# The function to get the data from firebase database.
# ====================================================================================================
def GetDatafromFirebase(db):
    results = db.child("data").get(user["idToken"]).val();  # needs the authorization to get the data.
    print("These are the records from the Database")
    print(results)
    return;


# The function to send the data to firebase database.
# ====================================================================================================
def sendtoFirebase(db, sensordata):
    result = db.child("data").push(sensordata, user["idToken"])  # needs the authorization to save the data
    print(result)
    return;

# The function to send the data to firebase database's user authorized section.
# Each user has a separate record tree, and it is only accessible for the authorized users.
# ====================================================================================================
def sendtoUserFirebase(db, sensordata):
    userid = user["localId"] # this will guarantee the data is stored into the user directory.
    result = db.child("userdata").child(userid).push(sensordata, user["idToken"])  # needs the authorization to save the data
    print(result)
    return;

# The function to set up the record structure to be written to the database.
# ====================================================================================================
def setupData(lux, tem, hum, uv, timestamp):
    sensor = {"Light": lux,
              "Temperature": tem,
              "Humidity": hum,
              "UV": uv,
              "timestamps": timestamp}  # always post the timestamps in epoch with the data to track the timing.
    # Store the data as the dictionary format in python  # refer to here:
    # https://www.w3schools.com/python/python_dictionaries.asp
    return sensor

#The following code is for AD YL-40 PCF8591 board. 
#==========================================================================
def mySensor():
    print ("Start of the record")
    count = 0
    firebase = dbInitialization()
    if (user != None):  # if authorization is not failed.
        while (1):
            sensordata = setupData(round(sensor_vem.lux,2),
                                   round(sensor_htu.temperature,2),
                                   round(sensor_htu.relative_humidity,2),
                                   (sensor_si1.readUV()/100.0),
                                   int(time.time()))    # this is the epoch time for this record.
            # we should send the data to the firebase. 
            # customize the sensordata before send the data out.    
            sendtoFirebase(firebase.database(), sensordata)  # save to the public access data tree
            sendtoUserFirebase(firebase.database(), sensordata) # save to the user specific userdata tree   
            count += 1
            sleep(5)  # delay for 5 seconds before next reading.
            if (count == 10):    # exit the program after 10 readings.
                break;
            GetDatafromFirebase(firebase.database())  # this statement is outside the while loop 
#Main program to read the A/D results from 4 channels on a YL40 board. 

def main():
    mySensor()
    return

if __name__=="__main__":
   main()
