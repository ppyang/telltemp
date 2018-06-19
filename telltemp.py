import serial
from time import sleep, strftime, time
import csv
import os
from datetime import datetime
import numpy
import matplotlib.pyplot as plt
# from drawnow import *
import sqlite3
from meteocalc import Temp, dew_point, heat_index
from math import exp

arduinoData = serial.Serial('com4', 9600)
tempArrary = []
humidityArray = []
old_temp = ''
old_humidity = ''
conn = sqlite3.connect('temp_and_humidity.db')
# plt.ion() #Tell matplotlib you watn interactive mode to plot live data

# def makeFigure():
#     plt.ylim(20, 90)
#     plt.plot(humidityArray, 'ro-', label="humidity")
#     plt.grid(True)
#     plt.ylabel('Humidity')
#     plt.legend(loc="upper left")
#
#     plt2 = plt.twinx()
#     plt.ylim(20, 35)
#     plt2.set_ylabel("Temperature")
#     plt2.plot(tempArrary, 'bo-', label="Temperature")
#     plt2.legend(loc="upper right")

def calculate_humidex(temp, humidity):
    # create input temperature in different units
    t = Temp(temp, 'c')  # c - celsius, f - fahrenheit, k - kelvin
    KELVIN = 273.16

    # calculate Dew Point
    dp = dew_point(temperature=t, humidity=humidity)+KELVIN-0.01

    # Calculate vapor pressure in mbar.
    e = 6.11 * exp(5417.7530 * ((1 / KELVIN) - (1 / dp)))

    h = 0.5555 * (e - 10.0)
    humidex = temp + h

    return round(humidex,1)
    # calculate Heat Index
    #hi = heat_index(temperature=t, humidity=humidity)

if __name__ == '__main__':

        # counter = 0
        while (True):
            try:
                if (arduinoData == None):
                    arduinoData = serial.Serial('com4', 9600)
                if (arduinoData.inWaiting()>0):
                    Linetext = arduinoData.readline()
                    readList = Linetext.split()
                    status = readList[0]
                    temperature = readList[1]
                    humidity = readList[2]
                    humidex = calculate_humidex(float(temperature),float(humidity) )
                    arduinoData.flushInput()
                    #plot the live data
                    # tempArrary.append(float(temperature))
                    # humidityArray.append(float(humidity))
                    # drawnow(makeFigure)
                    # plt.pause(0.000001)
                    try:
                        #write the data to a csv file
                        with open('temp_and_humidity.csv', 'a', newline='') as csvfile:
                            fieldnames = ['time', 'temperature', 'humidity', 'humidex']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            if os.stat("temp_and_humidity.csv").st_size == 0:
                                writer.writeheader()
                            now = datetime.now()
                            writer.writerow({'time':now.strftime('%Y/%m/%d %H:%M:%S'), 'temperature': temperature.decode(), 'humidity': (humidity+b"%").decode(), 'humidex': humidex})
                            csvfile.flush()
                            os.fsync(csvfile.fileno())
                            csvfile.close()
                        #print the data in terminal
                        print(status, temperature, humidity+b"%", humidex)
                    except EnvironmentError:
                        print("can't open the file. wait for another 5 min.")
                else:
                    continue


            except serial.SerialException:
                print(serial.SerialException)
                print ("Reading sensor error. retry connecting in 5 min")
                arduinoData.close()
                arduinoData = None

            #reset everything
            temperature = ''
            humidity = ''
            arduinoData.close()
            arduinoData = None
            sleep(300)
            # counter += 1
            # if counter > 20:
            #     tempArrary.pop(0)
            #     humidityArray.pop(0)
