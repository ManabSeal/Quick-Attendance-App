# Import required Libraries
import customtkinter as ctk
from PIL import Image
import cv2

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
import face_recognition

from sheets import updateGoogleSheet
import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "Your database URL",
    "storageBucket": "Your Storage bucket URL"
})


class1Start = datetime.time(10,0,0)
class1End = datetime.time(11,30,00)
class2Start = datetime.time(11,30,00)
class2End = datetime.time(13,00,00)

# Create an instance of TKinter Window or frame
win = ctk.CTk()
capture = False
# Set the size of the window
win.geometry("720x480")
win.title("Quick Attendance")
win.columnconfigure(0, weight=1)
win.rowconfigure(0, weight=2)
win.rowconfigure(1, weight=1)


#Creating camera frame(container)

cameraFrame = ctk.CTkFrame(win, height=360, width=480)
cameraFrame.grid(row=0, column=0,padx=10, pady=10, sticky="NEW",)

# Create a Label to capture the Video frames

webcamView =ctk.CTkLabel(cameraFrame)
webcamView.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
webcamView.configure(text="")
cap= cv2.VideoCapture(0)

def show_frames():
   # Get the latest frame and convert into Image
   #global capture
   cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
   """if capture is True:
      cv2.imwrite("l.jpg", cv2.cvtColor(cv2image, cv2.COLOR_RGB2BGR))
      capture = False
      print("captured")"""
   img = Image.fromarray(cv2image)
   # Convert image to PhotoImage
   #imgtk = ImageTk.PhotoImage(image = img)
   imgtk=ctk.CTkImage(img, size=(440,330))
   webcamView.imgtk = imgtk
   webcamView.configure(image=imgtk)
   # Repeat after an interval to capture continiously
   webcamView.after(20, show_frames)

def updateSemesterOptions(*args):
    if "MSC" in deptOptionVar.get():
        semesterOption.configure(values=semester_options[0:4])
    else:
        semesterOption.configure(values=semester_options)

def simple_popup1(img, name, roll, totalAttendacne):
   top = ctk.CTkToplevel(win)
   top.geometry("240x360")
   top.title("result")
   top.columnconfigure(0, weight=1)
   top.rowconfigure(0, weight=2)
   top.rowconfigure(1, weight=1)
   imgtk = Image.fromarray(img)
   imgtk=ctk.CTkImage(imgtk, size=(200, 200))
   imageFrame = ctk.CTkFrame(top, height=220, width=240)
   imageFrame.grid(row=0, column=0,padx=10, pady=10, sticky="NEW",)
   imageView =ctk.CTkLabel(imageFrame, image=imgtk, text="")
   imageView.imgtk = imgtk
   imageView.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
   labelsFrame = ctk.CTkFrame(top, height=180, width=240)
   labelsFrame.columnconfigure(0, weight=1)
   labelsFrame.grid(row=1, column=0, padx=10, pady=10, sticky="NEW")
   nameLabel = ctk.CTkLabel(labelsFrame, text="Name: " + name)
   nameLabel.grid(row=0, column=0)
   rollLabel = ctk.CTkLabel(labelsFrame, text="Roll No. : " + roll)
   rollLabel.grid(row=1, column=0)
   attendanceLabel = ctk.CTkLabel(labelsFrame, text="Total Attendance: " + str(totalAttendacne))
   attendanceLabel.grid(row=2, column=0)
   top.grab_set()

def simple_popup2(x):
   top = ctk.CTkToplevel(win)
   top.geometry("240x360")
   top.title("result")
   top.columnconfigure(0, weight=1)
   top.rowconfigure(0,weight=1)
   labelsFrame = ctk.CTkFrame(top, height=360, width=240)
   labelsFrame.grid(row=0, column=0, padx=10, pady=10, sticky="NEW")
   label = ctk.CTkLabel(labelsFrame, text=x)
   label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
   top.grab_set()

def checkMarked(time, day):
   if day == datetime.datetime.today().date() and (class1Start <= time < class1End or class2Start <= time <= class2End):
      print(datetime.datetime.today())
      return True
   return False


def validTime(time):
   weekday = datetime.datetime.today().weekday()
   """if time >= class1Start and time < class1End:
      return 2 if weekday == 6 else 0
   if time >= class2Start and time < class2End:
      return 2 if weekday == 6 else 1
   return 2"""
   if class1Start <= time < class1End:
      return 2 if weekday == 6 else 0
   if class2Start <= time < class2End:
      return 2 if weekday == 6 else 1
   return 2
   




bucket = storage.bucket()
blobs = bucket.list_blobs(prefix="MSC-CS/")
imgList = list(blobs)
def onClickButton():
   global imgList
   dataPath = f'{departmentOption.get()}/{semesterOption.get()}/'
   print(dataPath)
   if departmentOption.get() == "Select" or semesterOption.get() == "Select":
      simple_popup2("Please select valid options")
      return
   ref = db.reference(dataPath)
   data = ref.get()
   if not data:
      simple_popup2("Data Not Found")
      return
   print("Button Pressed")
   capImg = cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
   capImg = cv2.resize(capImg, (240,240))
   testFace = face_recognition.face_locations(capImg)
   print(testFace)
   if testFace:
      testEncode = face_recognition.face_encodings(capImg, testFace)
      
      minFaceDist = 2
      matchName = ""
      matchImage = ""
      """for img in imgList:
         #print(img.name)
         blob = bucket.get_blob(img.name)
         arr = np.frombuffer(blob.download_as_string(), np.uint8)
         curImg = cv2.imdecode(arr, cv2.COLOR_BGRA2RGB)
         curEncode = face_recognition.face_encodings(curImg)[0]
         print(face_recognition.face_distance(curEncode, testEncode))
         faceDist = face_recognition.face_distance(curEncode, testEncode)[0]
         if faceDist < minFaceDist:
            minFaceDist = faceDist
            matchName = img.name
            matchImage = curImg"""
      
      for x, y in data.items():
         curEncode = np.array(y["encoded_values"])
         faceDist = face_recognition.face_distance(curEncode, testEncode)[0]
         print(face_recognition.face_distance(curEncode, testEncode))
         if faceDist < minFaceDist:
            minFaceDist = faceDist
            matchName = x
      print(minFaceDist)
      if (minFaceDist > 0.55):
         simple_popup2("No matches found")
         return
      blob = bucket.get_blob(f'{departmentOption.get()}/{matchName}.jpg')
      print(blob)
      matchImage = np.frombuffer(blob.download_as_string(), np.uint8)
      matchImage = cv2.imdecode(matchImage, cv2.COLOR_BGRA2RGB)
      matchImage = cv2.cvtColor(matchImage, cv2.COLOR_RGB2BGR)
      print(matchName)
      matchedRoll = matchName
      data = data[matchName]
      #ref = db.reference(f'MSc/4/{matchedRoll}')
      
      studentDatetime = datetime.datetime.strptime(data['last_attendance'], '%Y-%m-%d %H:%M:%S')
      check = checkMarked(studentDatetime.time(), studentDatetime.date())
      if check is True:
         simple_popup2("You are marked.")
         return
      """secondsElapsed = (datetime.now() - studentDatetime).total_seconds()
      if secondsElapsed < 12000:
         simple_popup2("You are marked.")
         return
         datetime.datetime.now().time()
         """
      classtime = ""
      validity = validTime(datetime.time(11,52,23))
      print("validity", validity)
      if validity == 0:
         classtime = "10:00"
      elif validity == 1:
         classtime = "11:30"
      else:
         simple_popup2("Wrong Time/Day")
         return
      print("classtime", classtime)
      data['total_attendance'] += 1
      ref.child(f'{matchName}/total_attendance').set(data['total_attendance'])
      ref.child(f'{matchName}/last_attendance').set(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
      simple_popup1(matchImage, data['name'], matchedRoll, data['total_attendance'])
      updateGoogleSheet(matchedRoll, deptOptionVar.get(), classtime)
      
   else:
      simple_popup2("No Faces Found")
   #simple_popup("You are already marked")
#creating buttons container

def spaceKeypress(event):
   onClickButton()


buttonFrame = ctk.CTkFrame(win, height=200, width=480)
buttonFrame.grid(row=1, column=0, padx=10, pady=10, sticky="NEW")

button = ctk.CTkButton(buttonFrame, text="Capture(Space)", command=onClickButton)
button.place(relx=0.2, rely=0.5, anchor=ctk.CENTER)


department_options = ["BCA", "BHM", "BBA", "BSC-MLT", "MSC-CS", "MSC-MATHS"]
semester_options = ["1", "2", "3", "4", "5", "6"]
deptOptionVar = ctk.StringVar(buttonFrame)
deptOptionVar.set("Select")
semOptionVar = ctk.StringVar(buttonFrame)
semOptionVar.set("Select")

departmentOption = ctk.CTkOptionMenu(buttonFrame, values=department_options, variable=deptOptionVar)
departmentOption.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
deptOptionVar.trace("w", updateSemesterOptions)

semesterOption = ctk.CTkOptionMenu(buttonFrame, values=semester_options, variable=semOptionVar)
#semesterOption.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
semesterOption.place(relx=0.8, rely=0.5, anchor=ctk.CENTER)
# Define function to show frame

win.bind("<space>", spaceKeypress)
show_frames()
win.mainloop()