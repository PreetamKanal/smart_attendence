import cv2
import os
import numpy as np
import pickle
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime

# Firebase setup
cred = credentials.Certificate(r"C:\Users\Akshata\Downloads\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-a39da-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-a39da.appspot.com"
})

bucket = storage.bucket()

# Capture video from webcam
cap = cv2.VideoCapture(0)  # Use the correct camera index
cap.set(3, 640)  # Set the frame width
cap.set(4, 480)  # Set the frame height

imgBackground = cv2.imread('resources/background.jpg')

# Importing the mode images into a list
folderModePath = 'resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
print("Loading Encoded file...")
file = open('EncodeFile.p', 'rb')
encodingListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodingListKnownWithIds
print("Encode file loaded...")

modeType = 0
counter = 0
id = -1
imgStudent = []
studentInfo = {}

while True:
    success, img = cap.read()

    if not success:
        print("Failed to capture image")
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Resize the captured frame to fit the region on the background image
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # Add the mode image
    imgBackground[44:44 + 636, 808:808 + 417] = imgModeList[modeType]

    
    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]

            if counter == 0:
                cvzone.putTextRect(imgBackground, "Loading..", (275, 400))
                cv2.imshow("Face Attendance", imgBackground)
                cv2.waitKey(1)
                counter = 1 
                modeType = 1  # Set to loading mode

    if counter != 0:
        if counter == 1:
            # Get the data
            studentInfo = db.reference(f'students/{id}').get()
            print(studentInfo)
            # Get the image from the storage
            blob = bucket.get_blob(f'Images/{id}.jpg')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

            # Update data of attendance
            datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
            print(secondsElapsed)
            #if secondsElapsed > 30:
            ref = db.reference(f'students/{id}')
            studentInfo['total_attendance'] += 1
            ref.child('total_attendance').set(studentInfo['total_attendance'])
            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        
        #if modeType != 3:

        if 10<counter<20:
            modeType = 2
        
        imgBackground[44:44 + 636, 808:808 + 417] = imgModeList[modeType]

        
        
        if counter <= 10:   
            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo['year']), (1045, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
            offset = (414 - w) // 2
            cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
            #print("displayed")

        counter += 1

        if counter>=20:
            counter = 0
            modeType = 0
            studentInfo = []
            imgStudent = []
            imgBackground[44:44 + 636, 808:808 + 417] = imgModeList[modeType]


           
       
   
    # Display the images
    cv2.imshow("Face Attendance", imgBackground)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
