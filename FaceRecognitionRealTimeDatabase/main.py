import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-a522e-default-rtdb.firebaseio.com/",
    'storageBucket': 'faceattendancerealtime-a522e.appspot.com'
})

bucket = storage.bucket()

cap = cv2.VideoCapture(3)
cap.set(3,640)
cap.set(4,480)


imgBackground = cv2.imread('Resources/background.png')

#Importando las imagenes de mode en una lista.
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
#print(modePathList)

#cargar en archivo codificado.
print("Cargando Archivo Codificado ...")

file = open('EncodeFile.p', 'rb')
encodeListKnowWithIds = pickle.load(file)
file.close()
encodeListKnow, studentsIds = encodeListKnowWithIds
#print(studentsIds)
print("Archivo Codificado Completado")

modeType = 0
counter = 0
id = -1
imgStudent = []


while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0 ,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnow, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            #print("match Index", matchIndex)

            if matches[matchIndex]:
                # print("Rostro Conocido Detectado")
                # print(studentsIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentsIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Cargando...", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter!= 0:

           if counter ==1:
               #Obtenemos los datos
               studentInfo = db.reference(f'Students/{id}').get()
               print(studentInfo)
               #Obtenemos la imagen del almacen
               blob = bucket.get_blob(f'Images/{id}.png')
               array = np.frombuffer(blob.download_as_string(),np.uint8)
               imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
               #Actualizar la asistencia
               datetimeObject = datetime.strptime(studentInfo['hora_del_ultimo_registro'],
                                                 "%Y-%m-%d %H:%M:%S")
               secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
               print(secondsElapsed)
               if secondsElapsed >30:
                   ref = db.reference(f'Students/{id}')
                   studentInfo['asistencias_totales'] += 1
                   ref.child('asistencias_totales').set(studentInfo['asistencias_totales'])
                   ref.child('hora_del_ultimo_registro').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
               else:
                   modeType = 3
                   counter = 0
                   imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

           if modeType !=3:

                   if 10<counter<20:
                       modeType = 2

                   imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                   if counter <=10:
                       cv2.putText(imgBackground, str(studentInfo['asistencias_totales']),(861,125),
                                    cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                       cv2.putText(imgBackground, str(studentInfo['especialidad']), (1006, 550),
                                   cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                       cv2.putText(imgBackground, str(id), (1006, 493),
                                   cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                       cv2.putText(imgBackground, str(studentInfo['comportamiento']), (910, 625),
                                   cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                       cv2.putText(imgBackground, str(studentInfo['año']), (1025, 625),
                                   cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                       cv2.putText(imgBackground, str(studentInfo['año_inicio']), (1125, 625),
                                   cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                       (w, h), _ = cv2.getTextSize(studentInfo['nombre'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                       offset = (414 - w)//2
                       cv2.putText(imgBackground, str(studentInfo['nombre']), (808+offset, 445),
                                   cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                       imgBackground[175:175+216, 909:909+216] = imgStudent

                   counter+=1

                   if counter >=20:
                       counter = 0
                       modeType = 0
                       studentInfo = []
                       imgStudent = []
                       imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)