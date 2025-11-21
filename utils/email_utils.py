import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

import threading

def enviar_correo_async(destinatario, asunto, cuerpo):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Force IPv4 resolution
        import socket
        smtp_server = 'smtp.gmail.com'
        smtp_ip = socket.gethostbyname(smtp_server)
        
        with smtplib.SMTP(smtp_ip, 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error enviando correo: {e}")

def enviar_correo(destinatario, asunto, cuerpo):
    thread = threading.Thread(target=enviar_correo_async, args=(destinatario, asunto, cuerpo))
    thread.start()