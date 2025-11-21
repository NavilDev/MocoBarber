import base64
import os
import json
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_gmail_service():
    """Obtiene el servicio de Gmail autenticado."""
    creds = None
    
    # 1. Intentar cargar desde variable de entorno (Render)
    token_json = os.getenv("GOOGLE_TOKEN_JSON")
    if token_json:
        # Si es una ruta de archivo (Render Secret File)
        if os.path.exists(token_json):
             creds = Credentials.from_authorized_user_file(token_json, ['https://www.googleapis.com/auth/gmail.send'])
        else:
            # Si es el contenido JSON directo (menos común pero posible)
            try:
                info = json.loads(token_json)
                creds = Credentials.from_authorized_user_info(info, ['https://www.googleapis.com/auth/gmail.send'])
            except:
                print("Error parseando GOOGLE_TOKEN_JSON")

    # 2. Si no, intentar cargar localmente (Desarrollo)
    elif os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])

    # Refrescar si es necesario
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds:
        print("❌ No se encontraron credenciales válidas para Gmail.")
        return None

    return build('gmail', 'v1', credentials=creds)

def enviar_correo_async(destinatario, asunto, cuerpo):
    try:
        service = get_gmail_service()
        if not service:
            return

        message = MIMEMultipart()
        message['to'] = destinatario
        message['subject'] = asunto
        message.attach(MIMEText(cuerpo, 'plain'))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw_message}

        print(f"--- Iniciando envío de correo a {destinatario} (API Gmail) ---", flush=True)
        service.users().messages().send(userId='me', body=body).execute()
        print(f"✅ Correo enviado exitosamente a {destinatario}", flush=True)

    except Exception as e:
        print(f"❌ Error CRÍTICO enviando correo: {e}", flush=True)

def enviar_correo(destinatario, asunto, cuerpo):
    thread = threading.Thread(target=enviar_correo_async, args=(destinatario, asunto, cuerpo))
    thread.start()