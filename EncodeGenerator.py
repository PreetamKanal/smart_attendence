import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\Akshata\Downloads\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-a39da-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-a39da.appspot.com"
})

# Importing images from the folder into a list and uploading to Firebase Storage
folderPath = 'Images'
PathList = os.listdir(folderPath)
print(PathList)

imgList = []
studentIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)

# Function to find encodings for all images
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
        encode = face_recognition.face_encodings(img)
        if len(encode) > 0:
            encodeList.append(encode[0])

    return encodeList  # Moved out of the loop to ensure it returns after processing all images

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodingListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding complete")

# Saving the encodings along with student IDs
file = open("EncodeFile.p", 'wb')
pickle.dump(encodingListKnownWithIds, file)
file.close()
print("File saved")
