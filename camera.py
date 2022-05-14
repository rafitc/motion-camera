import cv2
import requests
import numpy as np
import time

face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor=0.6
API_URL = "https://secret-waters-79449.herokuapp.com"

def getFileName():
  obj = time.localtime() 
  today = str(obj.tm_year)+'-'+str(obj.tm_mon)+'-'+str(obj.tm_mday)+'-'+str(obj.tm_hour)+'-'+str(obj.tm_min)+'-'+str(obj.tm_sec)+".jpeg"
  return today

class VideoCamera(object):
    def __init__(self):
        self.count = 0
        self.static_back = None
        self.video = cv2.VideoCapture(1)
        success, image = self.video.read()
        x = requests.get(API_URL)
        if not x.status_code == 200:
            print("Cant connect to server. Check your network connection!")
            exit()
        print("Connected succesfully!")

        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        static_back = gray
        #static_back = gray
        # if static_back is None:
        #     static_back = gray
        #     print("got static back")
        #     pass
        #diff_frame = cv2.absdiff(static_back, gray)
    def __del__(self):
        self.video.release()
    #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
    def get_frame(self):
        success, image = self.video.read()
        motion = 0
        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if self.static_back is None:
            self.static_back = gray
            print("got static back")
            pass
        diff_frame = cv2.absdiff(self.static_back, gray)
        print("data frame")
        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)
        cnts,_ = cv2.findContours(thresh_frame.copy(),
                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts:
            if cv2.contourArea(contour) < 10000:
                continue
            motion = 1
            (x, y, w, h) = cv2.boundingRect(contour)
            # making green rectangle around the moving object
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            print("Motion detected : ", self.count)
            filename = getFileName()
            cv2.imwrite(filename, image)
            url = API_URL + "/detectedimage"
            files = {'file': open(filename, 'rb')}
            print("sending image to cloud")
            r = requests.post(url, files = files)
            print(r)
            self.count += 1

        # face_rects=face_cascade.detectMultiScale(gray,1.3,5)
        # for (x,y,w,h) in face_rects:
        # 	cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
        # 	break
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()