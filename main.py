# import the necessary packages
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time # Provides time-related functions
import cv2 # OpenCV library
import numpy as np # Import NumPy library
import requests

buzzer_pin, relay_one, relay_two = 13,19,26

print("Connecting to API")
#API_URL = "http://192.168.1.7:3000"
API_URL = "https://secret-waters-79449.herokuapp.com/"
x = requests.get(API_URL)
if not x.status_code == 200:
  print("Cant connect to server. Check your network connection!")
  exit()

print("Connected succesfully!")


print("GPIO init and turning on Fan")

import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(relay_one, GPIO.OUT)
GPIO.setup(relay_two, GPIO.OUT)
GPIO.setwarnings(False)
# while(1):
#   GPIO.output(26, GPIO.HIGH)
#   time.sleep(0.5);
#   GPIO.output(26, GPIO.LOW)
#   time.sleep(0.5)
#check the user activated motion detection or not 
while(1):
  break

def getFileName():
  obj = time.localtime() 
  today = str(obj.tm_year)+'-'+str(obj.tm_mon)+'-'+str(obj.tm_mday)+'-'+str(obj.tm_hour)+'-'+str(obj.tm_min)+'-'+str(obj.tm_sec)+".jpeg"
  return today

# Initialize the camera
print("Accessing Pi Camera")
#camera = PiCamera()
camera = cv2.VideoCapture(0)
ret, image = camera.read()
# Set the camera resolution
camera.resolution = (640, 480)
 
# Set the number of frames per second
camera.framerate = 30
 
# Generates a 3D RGB array and stores it in rawCapture
raw_capture = PiRGBArray(camera, size=(640, 480))
 
# Wait a certain number of seconds to allow the camera time to warmup
time.sleep(0.5)
 
# Initialize the first frame of the video stream
first_frame = None
 
# Create kernel for morphological operation. You can tweak
# the dimensions of the kernel.
# e.g. instead of 20, 20, you can try 30, 30
kernel = np.ones((20,20),np.uint8)
 
# Capture frames continuously from the camera
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
     
    # Grab the raw NumPy array representing the image
    image = frame.array
 
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     
    # Close gaps using closing
    gray = cv2.morphologyEx(gray,cv2.MORPH_CLOSE,kernel)
       
    # Remove salt and pepper noise with a median filter
    gray = cv2.medianBlur(gray,5)
     
    # If first frame, we need to initialize it.
    if first_frame is None:
         
      first_frame = gray
       
      # Clear the stream in preparation for the next frame
      raw_capture.truncate(0)
       
      # Go to top of for loop
      continue
       
    # Calculate the absolute difference between the current frame
    # and the first frame
    absolute_difference = cv2.absdiff(first_frame, gray)
 
    # If a pixel is less than ##, it is considered black (background). 
    # Otherwise, it is white (foreground). 255 is upper limit.
    # Modify the number after absolute_difference as you see fit.
    _, absolute_difference = cv2.threshold(absolute_difference, 100, 255, cv2.THRESH_BINARY)
 
    # Find the contours of the object inside the binary image
    contours, hierarchy = cv2.findContours(absolute_difference,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    areas = [cv2.contourArea(c) for c in contours]
  
    # If there are no countours
    if len(areas) < 1:
  
      # Display the resulting frame
      cv2.imshow('Frame',image)
  
      # Wait for keyPress for 1 millisecond
      key = cv2.waitKey(1) & 0xFF
  
      # Clear the stream in preparation for the next frame
      raw_capture.truncate(0)
     
      # If "q" is pressed on the keyboard, 
      # exit this loop
      if key == ord("q"):
        break
     
      # Go to the top of the for loop
      continue
  
    else:
         
      # Find the largest moving object in the image
      max_index = np.argmax(areas)
       
    # Draw the bounding box
    cnt = contours[max_index]
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),3)
  
    # Draw circle in the center of the bounding box
    x2 = x + int(w/2)
    y2 = y + int(h/2)
    cv2.circle(image,(x2,y2),4,(0,255,0),-1)
  
    # Print the centroid coordinates (we'll use the center of the
    # bounding box) on the image
    text = "x: " + str(x2) + ", y: " + str(y2)
    cv2.putText(image, text, (x2 - 10, y2 - 10),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
          
    # Display the resulting frame
    cv2.imshow("Frame",image)
    filename = getFileName()
    cv2.imwrite(filename, image)
    print("Motion detected!\n sending image to API")
    GPIO.output(buzzer_pin, GPIO.HIGH) #turning on buzzer 
    GPIO.output(relay_one, GPIO.HIGH) #Relay one turn on
    GPIO.output(relay_two, GPIO.HIGH) #Relay two turn on
    url = API_URL+"/detectedimage"
    files = {'file': open(filename, 'rb')}
    r = requests.post(url, files = files)
    print(r)
    # Wait for keyPress for 1 millisecond
    key = cv2.waitKey(1) & 0xFF
  
    # Clear the stream in preparation for the next frame
    raw_capture.truncate(0)

    #turn of and ready for next event 
    time.sleep(0.5)
    GPIO.output(buzzer_pin, GPIO.LOW) #turning on buzzer 
    GPIO.output(relay_one, GPIO.LOW) #Relay one turn on
    GPIO.output(relay_two, GPIO.LOW) #Relay two turn on
     
    # If "q" is pressed on the keyboard, 
    # exit this loop

    if key == ord("q"):
      break
 
# Close down windows
cv2.destroyAllWindows()