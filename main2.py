from typing import Optional, Tuple, Union
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import io
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np

import tkinter as tk
from tkinter import ttk
import csv
import os
from datetime import datetime


from sheets import inserIntoGoogleSheet, changeGoogleSheet

cred = credentials.Certificate("your_firebase_service_account_creds.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "Your database URL",
    "storageBucket": "Your storage bucket URL"
})



"""def simple_popup2(win, x):
   top = ctk.CTkToplevel(win)
   top.geometry("240x360")
   top.title("result")
   top.columnconfigure(0, weight=1)
   top.rowconfigure(0,weight=1)
   labelsFrame = ctk.CTkFrame(top, height=360, width=240)
   labelsFrame.grid(row=0, column=0, padx=10, pady=10, sticky="NEW")
   label = ctk.CTkLabel(labelsFrame, text=x)
   label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
   top.grab_set()"""

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        
        self.add("Upload Data")  # add tab at the end
        self.add("Show Data")  # add tab at the end
        self.set("Upload Data")  # set currently visible
        
        self.tab("Upload Data").rowconfigure(0, weight=1)  # configure grid system
        self.tab("Upload Data").columnconfigure(0,weight=1)
        self.tab("Show Data").rowconfigure(0, weight=1)  # configure grid system
        self.tab("Show Data").columnconfigure(0,weight=1)

        # add widgets on tabs
        self.mainFrame1 = UploadScreen(master=self.tab("Upload Data"))
        self.mainFrame1.grid(row=0, column=0,padx = 10, pady = 10, sticky="nsew")

        self.mainFrame3 = ShowData(master=self.tab("Show Data"))
        self.mainFrame3.grid(row=0, column=0,padx = 10, pady = 10, sticky="nsew")
    def refreshUpload(self):
        self.mainFrame1.destroy()
        self.mainFrame1 = UploadScreen(master=self.tab("Upload Data"))
        self.mainFrame1.grid(row=0, column=0,padx = 10, pady = 10, sticky="nsew")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.title("Quick Attendance Upload")
        self.rowconfigure(0, weight=1)  # configure grid system
        self.columnconfigure(0, weight=1)

        self.tab_view = MyTabView(master=self, height=600, width=800)
        self.tab_view.grid(row=0, column=0,padx=10, pady=10, sticky="nsew")
        






class UploadScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        self.encoded_img = np.array([0,1,2,3])
        self.bs = io.BytesIO()
        department_options = ["BCA", "BHM", "BBA", "BSC-MLT", "MSC-CS", "MSC-MATHS"]
        semester_options = ["1", "2", "3", "4", "5", "6"]
        deptOptionVar = ctk.StringVar(self)
        deptOptionVar.set("Select")
        semOptionVar = ctk.StringVar(self)
        semOptionVar.set("Select")


        def updateSemesterOptions(*args):
            if "MSC" in deptOptionVar.get():
                semesterOption.configure(values=semester_options[0:4])
            else:
                semesterOption.configure(values=semester_options)


        
        def uploadFile():
            self.bs = io.BytesIO()
            f_types = [('Jpg Files', '*.jpg')]
            fileName = ctk.filedialog.askopenfilename(filetypes=f_types)
            if not fileName:
                return
            print(fileName)
            img = Image.open(fileName)
            cvImg = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            img = img.resize((240,240))
            self.encoded_img = face_recognition.face_encodings(cvImg)
            #print(encoded_img)
            imgResized = ctk.CTkImage(img, size=(150,150))
            img.save(self.bs, "jpeg")
            imageLabel.configure(text="", image=imgResized)

        def uploadAllData():
            dbRef = db.reference(departmentOptions.get()+"/"+semesterOption.get())
            if not isinstance(self.encoded_img, list):
                popup = SimplePopup("Select Valid Image")
                return
            if self.encoded_img == []:
                popup = SimplePopup("Select Valid Image")
                return
            if dbRef.child(rollEntry.get()).get():
                popup = SimplePopup("Student Already Exists")
                return
            allData = dbRef.get()

            if allData:
                minFaceDist = 2
                for x, y in allData.items():
                    curEncode = np.array(y["encoded_values"])
                    faceDist = face_recognition.face_distance(curEncode, self.encoded_img)[0]
                    print(face_recognition.face_distance(curEncode, self.encoded_img))
                    if faceDist < minFaceDist:
                        minFaceDist = faceDist
                        matchRoll = x
                        matchName = y["name"]
                print(minFaceDist)
                if (minFaceDist < 0.2):
                    popup = SimplePopup(f'{matchName},{matchRoll}', 'already exists')
                    return
                
            studentDetails = {
                    "last_attendance": "1970-01-01 12:00:00",
                    "name": nameEntry.get(),
                    "stream": deptOptionVar.get(),
                    "total_attendance": 0,
                    "encoded_values": self.encoded_img[0].tolist()
                }
            dbRef.child(rollEntry.get()).set(studentDetails)
            print(self.encoded_img)
            inserIntoGoogleSheet(rollEntry.get(), nameEntry.get(), deptOptionVar.get())
            #db.reference(studentDetails["stream"]+"/"+rollEntry.get()).child("encode").set(encoded_img.tolist())
            bucket = storage.bucket()
            blob = bucket.blob(departmentOptions.get()+"/"+rollEntry.get()+".jpg")
            blob.upload_from_string(self.bs.getvalue(), content_type="image/jpeg")
            print(studentDetails)            
            app.tab_view.refreshUpload()

        
        nameLabel = ctk.CTkLabel(self, text="Name")
        nameLabel.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        nameEntry = ctk.CTkEntry(self, placeholder_text="Enter Student's Name")
        nameEntry.grid(row=0, column=1, columnspan=10, padx=15, pady=15, sticky="ew")

        rollLabel = ctk.CTkLabel(self, text="Roll No.")
        rollLabel.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        rollEntry = ctk.CTkEntry(self, placeholder_text="Enter Roll Number")
        rollEntry.grid(row=1, column=1, padx=15, pady=15, sticky="ew")

        departmentLabel = ctk.CTkLabel(self, text="Department")
        departmentLabel.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        departmentOptions = ctk.CTkOptionMenu(self, values=department_options, variable=deptOptionVar)
        departmentOptions.grid(row=2, column=1, padx=15, pady=15, sticky="ew")
        deptOptionVar.trace("w", updateSemesterOptions)

        semesterLabel = ctk.CTkLabel(self, text="Semester")
        semesterLabel.grid(row=3, column=0, padx=15, pady=15, sticky="ew")
        semesterOption = ctk.CTkOptionMenu(self, values=semester_options, variable=semOptionVar)
        semesterOption.grid(row=3, column=1, padx=15, pady=15, sticky="ew")

        imageLabel = ctk.CTkLabel(self, text="Image")
        imageLabel.grid(row=4, column=0, padx=15, pady=15, sticky="ew")
        uploadButton = ctk.CTkButton(self, text="Browse Image", command=uploadFile)
        uploadButton.grid(row=4, column=1, padx=15, pady=15, sticky="ew")

        submitButton = ctk.CTkButton(self, text="Submit", command=uploadAllData)
        submitButton.grid(row=5, column=0, columnspan=3, padx=15, pady=15, sticky="S")
    


class ShowData(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure((1,2,3,4), weight=1)
        self.rowconfigure(1, weight=4)

        self.obj = {}
        department_options = ["BCA", "BHM", "BBA", "BSC-MLT", "MSC-CS", "MSC-MATHS"]
        semester_options = ["1", "2", "3", "4", "5", "6"]
        attendance_options = ["All",">10","<10","<2"]
        rollVar = ctk.StringVar(value="")
        deptOptionVar = ctk.StringVar(self)
        deptOptionVar.set("Select")
        semOptionVar = ctk.StringVar(self)
        semOptionVar.set("Select")
        attendanceOptionVar = ctk.StringVar(self)
        attendanceOptionVar.set("All")


        def updateSemesterOptions(*args):
            if "MSC" in deptOptionVar.get():
                semesterOption.configure(values=semester_options[0:4])
            else:
                semesterOption.configure(values=semester_options)
            if deptOptionVar.get() != "Select" and semOptionVar.get() != "Select":
                path = db.reference(f'{deptOptionVar.get()}/{semOptionVar.get()}')
                att = attendanceOptionVar.get()
                data = path.get()
                self.obj = {}
                if att == "<2" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 2:
                            self.obj[x] = y
                elif att == ">10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) > 10:
                            self.obj[x] = y
                elif att == "<10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 10:
                            self.obj[x] = y
                elif att == "All" and data:
                    self.obj = data
            #print(self.obj)
            self.createTable(self.obj)

        def onSemChange(*args):
            if deptOptionVar.get() == "Select":
                return
            else:
                path = db.reference(f'{deptOptionVar.get()}/{semOptionVar.get()}')
                att = attendanceOptionVar.get()
                data = path.get()
                self.obj = {}
                if att == "<2" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 2:
                            self.obj[x] = y
                elif att == ">10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) > 10:
                            self.obj[x] = y
                elif att == "<10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 10:
                            self.obj[x] = y
                elif att == "All" and data:
                    self.obj = data
            #print(self.obj)
            self.createTable(self.obj)
        
        def onAttendanceChange(*args):
            if deptOptionVar.get() == "Select" or semOptionVar.get() == "Select":
                return
            else:
                path = db.reference(f'{deptOptionVar.get()}/{semOptionVar.get()}')
                att = attendanceOptionVar.get()
                data = path.get()
                self.obj = {}
                if att == "<2" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 2:
                            self.obj[x] = y
                elif att == ">10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) > 10:
                            self.obj[x] = y
                elif att == "<10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 10:
                            self.obj[x] = y
                elif att == "All" and data:
                    self.obj = data
            #print(self.obj)
            self.createTable(self.obj)


        def downloadCSV():
            #print("download")
            if deptOptionVar.get() != "Select" and semOptionVar.get() != "Select": 
                path = os.path.join(os.getcwd(), "downloads")
                if not os.path.exists(path):
                    os.mkdir(path)
                fields = ["Roll", "Name", "Last Attended", "Total Attendance"]
                fileName = deptOptionVar.get()+"-"+semOptionVar.get()+"-"+datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + ".csv"
                fullPath = os.path.join(path, fileName)
                with open(fullPath, 'w', newline="") as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(fields)
                    for item in self.tree.get_children():
                        data = self.tree.item(item)
                        csvwriter.writerow(data["values"])


            
        def onRollChange(*args):
            print("changing")
            if deptOptionVar.get() == "Select" or semOptionVar.get() == "Select":
                return
            else:
                att = attendanceOptionVar.get()
                roll = rollVar.get()
                data = self.obj
                obj = {}
                if att == "<2" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 2 and str(x).startswith(roll):
                            obj[x] = y
                elif att == ">10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) > 10 and str(x).startswith(roll):
                            obj[x] = y
                elif att == "<10" and data:
                    for x,y in data.items():
                        if int(y["total_attendance"]) < 10 and str(x).startswith(roll):
                            obj[x] = y
                elif att == "All" and data:
                    for x,y in data.items():
                        if str(x).startswith(roll):
                            obj[x] = y
            #print(self.obj)
            self.createTable(obj)
            
                
       
        rollEntry = ctk.CTkEntry(self, placeholder_text="Roll", textvariable=rollVar)
        rollEntry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        rollVar.trace('w', onRollChange)

        departmentOptions = ctk.CTkOptionMenu(self, values=department_options, variable=deptOptionVar)
        departmentOptions.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        deptOptionVar.trace("w", updateSemesterOptions)

        semesterOption = ctk.CTkOptionMenu(self, values=semester_options, variable=semOptionVar)
        semesterOption.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        semOptionVar.trace("w", onSemChange)

        attendanceOption = ctk.CTkOptionMenu(self, values=attendance_options, variable=attendanceOptionVar)
        attendanceOption.grid(row=0, column=3, padx=10, pady=10,sticky="ew")
        attendanceOptionVar.trace("w", onAttendanceChange)

        downloadButton = ctk.CTkButton(self, text="Download CSV", command=downloadCSV)
        downloadButton.grid(row=0, column=4, padx=10, pady=10, sticky="ew")


        columns = ('roll', 'name', 'last_attendance','total_attendance')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('roll', text='Roll No.')
        self.tree.heading('name', text='Name')
        self.tree.heading('last_attendance', text='Last Attendance')
        self.tree.heading('total_attendance', text='Total Attendance')
        self.tree.column("roll",anchor="center", stretch=tk.NO, width=100)
        self.tree.column("name",anchor="center")
        self.tree.column("last_attendance",anchor="center")
        self.tree.column("total_attendance",anchor="center")
        self.tree.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')
        scrollbar = ctk.CTkScrollbar(self, orientation=ctk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=5, sticky='ns')
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
            background="#2a2d2e",
            foreground="white",
            rowheight=25,
            fieldbackground="#343638",
            bordercolor="#343638",
            borderwidth=1)
        style.map('Treeview', background=[('selected', '#22559b')])
        
        style.configure("Treeview.Heading",
            background="#565b5e",
            foreground="white",
            relief="flat")
        style.map("Treeview.Heading",
            background=[('active', '#3484F0')])

        #tableFrame = ctk.CTkFrame(self)
        def onDoubleClick(event):
            item = self.tree.selection()
            #print(self.tree.item(item, 'values'))
            temp = self.tree.item(item, 'values')
            data = {
                "roll": temp[0],
                "name": temp[1],
                "last_attendance": temp[2],
                "total_attendance": int(temp[3]),
                "department": deptOptionVar.get(), 
                "semester": semOptionVar.get(),
                "encoded_values": self.obj[temp[0]]["encoded_values"]
            }
            print(data)
            openUpdate = UpdatePopup(data)
        self.tree.bind('<Double-1>', onDoubleClick)

    def createTable(self, obj):
            for item in self.tree.get_children():
                self.tree.delete(item)
            for x,y in obj.items():
                value = (x, y["name"], y["last_attendance"], y["total_attendance"])
                self.tree.insert('', tk.END, values=value)

class SimplePopup(ctk.CTkToplevel):
    def __init__(self,x,y=None,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("240x360")
        self.title("result")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1)
        labelsFrame = ctk.CTkFrame(self, height=360, width=240)
        labelsFrame.grid(row=0, column=0, padx=10, pady=10, sticky="NEW")
        label = ctk.CTkLabel(labelsFrame, text=x)
        label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        if y:
            label2 = ctk.CTkLabel(labelsFrame, text=y)
            label2.place(relx=0.5, rely = 0.6, anchor=ctk.CENTER)
        self.grab_set()


class UpdatePopup(ctk.CTkToplevel):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("720x480")
        self.title(data["name"])
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        department_options = ["BCA", "BHM", "BBA", "BSC-MLT", "MSC-CS", "MSC-MATHS"]
        semester_options = ["1", "2", "3", "4", "5", "6"]
        self.deptOptionVar = ctk.StringVar(self)
        self.deptOptionVar.set(data["department"])
        self.semOptionVar = ctk.StringVar(self)
        self.semOptionVar.set(data["semester"])
        self.nameVar = ctk.StringVar(self)
        self.nameVar.set(data["name"])
        self.encoded_values = [np.array(data["encoded_values"])]
        self.encodeChange = False
        print(type(self.encoded_values))
        self.bs = io.BytesIO()


        def updateSemesterOptions(*args):
            if "MSC" in self.deptOptionVar.get():
                semesterOption.configure(values=semester_options[0:4])
            else:
                semesterOption.configure(values=semester_options)

        def uploadFile():
            self.bs = io.BytesIO()
            f_types = [('Jpg Files', '*.jpg')]
            fileName = ctk.filedialog.askopenfilename(filetypes=f_types)
            if not fileName:
                return
            print(fileName)
            img = Image.open(fileName)
            cvImg = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            img = img.resize((240,240))
            self.encoded_values = face_recognition.face_encodings(cvImg)
            if self.encoded_values:
                self.encodeChange = True
            print(type(self.encoded_values))
            #print(encoded_img)
            imgResized = ctk.CTkImage(img, size=(150,150))
            img.save(self.bs, "jpeg")
            imageLabel.configure(text="", image=imgResized)
        
        def updateAllData():
            dbRef = db.reference(self.deptOptionVar.get()+"/"+self.semOptionVar.get())
            
            allData = dbRef.get()

            if allData and self.encodeChange:
                minFaceDist = 2
                for x, y in allData.items():
                    curEncode = np.array(y["encoded_values"])
                    faceDist = face_recognition.face_distance(curEncode, self.encoded_values)[0]
                    print(face_recognition.face_distance(curEncode, self.encoded_values))
                    if faceDist < minFaceDist:
                        minFaceDist = faceDist
                        matchRoll = x
                        matchName = y["name"]
                print(minFaceDist)
                if (minFaceDist < 0.2):
                    popup = SimplePopup(f'{matchName},{matchRoll}', 'already exists')
                    return

            studentData = {
                    "name": self.nameVar.get(),
                    "stream": self.deptOptionVar.get(),
                    "last_attendance": data["last_attendance"],
                    "total_attendance": int(data["total_attendance"]),
                    "encoded_values": self.encoded_values[0].tolist() 
            }
            db.reference(f'{data["department"]}/{data["semester"]}/{data["roll"]}').delete()
            if self.encodeChange:
                bucket = storage.bucket()
                blob = bucket.blob(data["department"]+"/"+data["roll"]+".jpg")
                blob.delete()
                blob = bucket.blob(self.deptOptionVar.get()+"/"+data["roll"]+".jpg")
                blob.upload_from_string(self.bs.getvalue(), content_type="image/jpeg")
            elif data["department"] != self.deptOptionVar.get():
                bucket = storage.bucket()
                blob = bucket.blob(data["department"]+"/"+data["roll"]+".jpg")
                file = blob.download_as_string()
                blob.delete()
                blob = bucket.blob(self.deptOptionVar.get()+"/"+data["roll"]+".jpg")
                blob.upload_from_string(file, content_type="image/jpeg")
                changeGoogleSheet(data["roll"], studentData["name"], data["department"], studentData["stream"])
                del app.tab_view.mainFrame3.obj[data["roll"]]
                app.tab_view.mainFrame3.createTable(app.tab_view.mainFrame3.obj)
            db.reference(f'{self.deptOptionVar.get()}/{self.semOptionVar.get()}').child(data["roll"]).set(studentData)
            self.destroy()
            #app.tab_view.mainFrame3.self.tree.createTable()

        rollLabel = ctk.CTkLabel(self, text="Roll No. :     " + data["roll"], font=("Helvetica", 20))
        rollLabel.grid(row=0, column=0,columnspan=2, padx=10, pady=10, sticky="ew")

        nameLabel = ctk.CTkLabel(self, text="Name")
        nameLabel.grid(row=1, column=0, padx=15, pady=15, sticky="ew")
        nameEntry = ctk.CTkEntry(self, placeholder_text="Enter Student's Name", textvariable=self.nameVar)
        nameEntry.grid(row=1, column=1, padx=15, pady=15, sticky="ew")

        departmentLabel = ctk.CTkLabel(self, text="Department")
        departmentLabel.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        departmentOptions = ctk.CTkOptionMenu(self, values=department_options, variable=self.deptOptionVar)
        departmentOptions.grid(row=2, column=1, padx=15, pady=15, sticky="ew")
        self.deptOptionVar.trace("w", updateSemesterOptions)

        semesterLabel = ctk.CTkLabel(self, text="Semester")
        semesterLabel.grid(row=3, column=0, padx=15, pady=15, sticky="ew")
        semesterOption = ctk.CTkOptionMenu(self, values=semester_options, variable=self.semOptionVar)
        semesterOption.grid(row=3, column=1, padx=15, pady=15, sticky="ew")

        bucket = storage.bucket()
        blob = bucket.get_blob(f'{data["department"]}/{data["roll"]}.jpg')
        img = np.frombuffer(blob.download_as_string(), np.uint8)
        img = cv2.imdecode(img, cv2.COLOR_BGRA2RGB)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        imgtk = Image.fromarray(img)
        imgtk=ctk.CTkImage(imgtk, size=(150, 150))
        
        imageLabel = ctk.CTkLabel(self, image = imgtk, text="")
        imageLabel.imgtk = imgtk
        imageLabel.grid(row=4, column=0, padx=15, pady=15, sticky="ew")
        uploadButton = ctk.CTkButton(self, text="Browse Image",command=uploadFile)
        uploadButton.grid(row=4, column=1, padx=15, pady=15, sticky="ew")

        submitButton = ctk.CTkButton(self, text="Submit", command=updateAllData)
        submitButton.grid(row=5, column=0, columnspan=3, padx=15, pady=15, sticky="S")
        self.grab_set()

        

app = App()
app.mainloop()