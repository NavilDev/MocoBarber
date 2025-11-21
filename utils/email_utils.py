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
        print(f"--- Iniciando envío de correo a {destinatario} ---")
        # Force IPv4 resolution
        import socket
        smtp_server = 'smtp.gmail.com'
        smtp_ip = socket.gethostbyname(smtp_server)
        print(f"IP resuelta para smtp.gmail.com: {smtp_ip}", flush=True)
        
        print("Conectando al servidor SMTP (SSL)...", flush=True)
        with smtplib.SMTP_SSL(smtp_ip, 465, timeout=30) as server:
            server.set_debuglevel(1) 
            print("Iniciando sesión...", flush=True)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print("Enviando mensaje...", flush=True)
            server.send_message(msg)
        print(f"✅ Correo enviado exitosamente a {destinatario}", flush=True)
    except Exception as e:
        print(f"❌ Error CRÍTICO enviando correo: {e}", flush=True)

def enviar_correo(destinatario, asunto, cuerpo):
    thread = threading.Thread(target=enviar_correo_async, args=(destinatario, asunto, cuerpo))
    thread.start()