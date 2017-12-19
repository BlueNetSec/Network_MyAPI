from flask import Flask, render_template, jsonify, request
import datetime
import RPi.GPIO as GPIO
app = Flask(__name__)
from six.moves import input
from zeroconf import ServiceBrowser, Zeroconf
import socket


currentColor = "off"
currentStatus = "off"
currentIntensity = "0"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
R = GPIO.PWM(12, 100)
GPIO.setup(16, GPIO.OUT)
G = GPIO.PWM(16, 100)
GPIO.setup(18, GPIO.OUT)
B = GPIO.PWM(18, 100)

def setLEDColor(status, color, intensity):
    if status == "off":
        returnStatement = "Turned off"
        R.start(0)
        G.start(0)
        B.start(0)
    elif int(intensity)  > -1 and int(intensity) < 101 and status == "on":
        if color == "red":
           returnStatement = "Color updated"
           R.start(int(intensity))
           G.start(0)
           B.start(0)
        elif color == "blue":
           returnStatement = "Color updated"
           R.start(0)
           G.start(0)
           B.start(int(intensity))
        elif color == "green":
            returnStatement = "Color updated"
            R.start(0)
            G.start(int(intensity))
            B.start(0)
        elif color == "magenta":
            returnStatement = "Color updated"
            R.start(int(intensity))
            G.start(0)
            B.start(int(intensity))
        elif color == "cyan":
            returnStatement = "Color updated"
            R.start(0)
            G.start(int(intensity))
            B.start(int(intensity))
        elif color == "yellow":
            returnStatement = "Color updated"
            R.start(int(intensity))
            G.start(int(intensity))
            B.start(0)
        elif color == "white":
            returnStatement = "Color updated"
            R.start(int(intensity))
            G.start(int(intensity))
            B.start(int(intensity))
        else:
            returnStatement = "You gave an invalid color"
            R.start(0)
            G.start(0)
            B.start(0)
    else:
          returnStatement = "Invalid values"
    return returnStatement

def setCurrentValues(colorValue, statusValue, intensityValue):
    global currentStatus
    global currentColor
    global currentIntensity
    
    if colorValue is not None and statusValue is not None and intensityValue is not None:
        currentColor= colorValue
        currentStatus = statusValue
        currentIntensity = intensityValue
    else:
        currentStatus = "off"
        currentIntensity = "0"
        currentColor = "off"

@app.route("/LED", methods=['GET'])
def get_values():
    data = ("Status: " + currentStatus + " Color: " + currentColor + " Intensity: " + currentIntensity)
    return data

@app.route("/LED", methods=['POST'])
def set_values():
    statusValue = request.args.get('status')
    colorValue = request.args.get('color')
    intensityValue = request.args.get('intensity')
    setCurrentValues(colorValue, statusValue, intensityValue)
    returnStatement = setLEDColor(statusValue, colorValue, intensityValue)
    return returnStatement

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
