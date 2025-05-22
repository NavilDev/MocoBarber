from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def crear_evento(nombre, telefono, fecha, hora, archivo_credenciales, calendar_id):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(
        archivo_credenciales, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    inicio = f"{fecha}T{hora}:00"
    hora_dt = datetime.strptime(hora, "%H:%M")
    hora_fin_dt = hora_dt + timedelta(minutes=30)
    hora_fin = hora_fin_dt.strftime("%H:%M")
    fin = f"{fecha}T{hora_fin}:00"

    evento = {
        'summary': f'Cita con {nombre}',
        'description': f'Teléfono: {telefono}',
        'start': {'dateTime': inicio, 'timeZone': 'Europe/Madrid'},
        'end': {'dateTime': fin, 'timeZone': 'Europe/Madrid'},
    }

    evento = service.events().insert(calendarId=calendar_id, body=evento).execute()
    print(f"✅ Evento creado: {evento.get('htmlLink')}")