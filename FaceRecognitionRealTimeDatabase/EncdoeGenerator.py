import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-a522e-default-rtdb.firebaseio.com/",
    'storageBucket': 'faceattendancerealtime-a522e.appspot.com'
})

#Importando las imagenes de estudiantes en una lista.
folderPath = 'Images'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
studentsIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentsIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

    # print(path)
    # print(os.path.splitext(path)[0])
print(studentsIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList
print("Encoding Started...")
encodeListKnow = findEncodings(imgList)
encodeListKnowWithIds = [encodeListKnow, studentsIds]
#print(encodeListKnow)
print("Encoding Complete")

file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnowWithIds,file)
file.close()
print("File Saved")