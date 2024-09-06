import firebase_admin
from firebase_admin import credentials, db

# Correct path to your service account key
cred = credentials.Certificate(r"C:\Users\Akshata\Downloads\serviceAccountKey.json")

# Initialize the Firebase app
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-a39da-default-rtdb.firebaseio.com/"
})

# Reference to the students node in the database
ref = db.reference('students')

# Data to be added to the database
#dictionary format data
data = {
    "12345": {
        "name": "Akshata Dhagade",
        "major": "ECE",
        "starting_year": 2019,
        "total_attendance": 0,
        "standing": "Average",
        "year": 3,
        "last_attendance_time": "2024-12-11 00:54:34"
    },
    "67890": {
        "name": "Bhagyashree",
        "major": "Information Science",
        "starting_year": 2019,
        "total_attendance": 0,
        "standing": "Good",
        "year": 3,
        "last_attendance_time": "2024-12-11 00:54:34"
    },
    "21223": {
        "name": "Preetam",
        "major": "ECE",
        "starting_year": 2019,
        "total_attendance": 0,
        "standing": "Average",
        "year": 3,
        "last_attendance_time": "2024-12-11 00:54:34"
    },
    "22234": {
        "name": "Pavan",
        "major": "ECE",
        "starting_year": 2019,
        "total_attendance": 0,
        "standing": "Excellent",
        "year": 3,
        "last_attendance_time": "2024-12-11 00:54:34"
    }

}

# Adding data to the database
for key, value in data.items():
    ref.child(key).set(value)

print("Data has been successfully added to the database.")
