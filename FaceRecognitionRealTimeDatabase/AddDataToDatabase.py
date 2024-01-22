import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-a522e-default-rtdb.firebaseio.com/"

})
ref = db.reference('Students')

data = {
    "112233":
        {
            "nombre": "Ryan Gosling",
            "especialidad": "Robotics",
            "año_inicio": 2017,
            "asistencias_totales": 2,
            "comportamiento": "G",
            "año": 6,
            "hora_del_ultimo_registro": "2023-09-09 00:11:20"
        },
    "223344":
        {
            "nombre": "Ana De Armas",
            "especialidad": "Graphics",
            "año_inicio": 2019,
            "asistencias_totales": 12,
            "comportamiento": "V",
            "año": 4,
            "hora_del_ultimo_registro": "2023-09-09 00:11:20"
        },
    "334455":
        {
            "nombre": "Hamilton Perez",
            "especialidad": "Development",
            "año_inicio": 2020,
            "asistencias_totales": 8,
            "comportamiento": "W",
            "año": 3,
            "hora_del_ultimo_registro": "2023-09-09 00:11:20"
        },
    "445566":
        {
            "nombre": "Barbara Espinosa",
            "especialidad": "Data Bases",
            "año_inicio": 2020,
            "asistencias_totales": 8,
            "comportamiento": "W",
            "año": 3,
            "hora_del_ultimo_registro": "2023-09-09 00:11:20"
        },
    "556677":
        {
            "nombre": "Erick Riascos",
            "especialidad": "Development",
            "año_inicio": 2020,
            "asistencias_totales": 8,
            "comportamiento": "W",
            "año": 3,
            "hora_del_ultimo_registro": "2023-09-09 00:11:20"
        },
}

for key,value in data.items():
    ref.child(key).set(value)