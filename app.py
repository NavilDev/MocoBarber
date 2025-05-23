import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy, text
from datetime import datetime
from config import HORARIOS_DISPONIBLES, DURACIONES_SERVICIOS
from utils.email_utils import enviar_correo
from utils.horarios import obtener_horarios_disponibles
from crear_evento_calendar import crear_evento
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import timedelta  
from config import DURACIONES_SERVICIOS
from datetime import datetime, timedelta
import json
import os



# Cargar las variables del .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fecha = db.Column(db.String(10))
    hora = db.Column(db.String(5))
    servicio = db.Column(db.String(50))
    event_id = db.Column(db.String(255))  # ID del evento en Google Calendar

   


    SCOPES = ['https://www.googleapis.com/auth/calendar']
    with open(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"), "r") as f:
        service_account_info = json.load(f)    
        credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)

    

# Rutas
@app.route("/citas", methods=["GET", "POST"])
def citas():
    if request.method == "POST":
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        email = request.form['email']
        fecha = request.form['fecha']
        hora = request.form['hora']
        servicio = request.form['servicio']

        # Validación
        existente = Reserva.query.filter_by(fecha=fecha, hora=hora).first()
        if existente:
            return render_template("error.html", mensaje="Este horario ya fue reservado.")
        
        event_id = crear_evento(
        nombre=nombre,
        telefono=telefono,
        fecha=fecha,
        hora=hora,
        servicio=servicio,
        archivo_credenciales=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"),
        calendar_id="Mocobarber032@gmail.com"
    )
        

        # Guarda los registros en la base de datos
        nueva = Reserva(nombre=nombre, telefono=telefono,email=email, fecha=fecha, hora=hora, servicio=servicio, event_id=event_id)
        db.session.add(nueva)
        db.session.commit()

        # Enviar correos
        asunto = " ¡Tu cita está confirmada! 💈"
        cuerpo_cliente = f'''¡Gracias por reservar tu cita conmigo en MocoBarber!

📅 Fecha: {fecha}
🕒 Hora: {hora}

Ya tengo todo listo para recibirte y asegurarme de que salgas con el mejor corte y una gran experiencia.

Si necesitas cambiar tu cita o tienes alguna duda, puedes escribirme directamente.

¡Nos vemos pronto en la silla! ✂️

Un saludo'''
        

        
        
        cuerpo_barbero = f"📅 Nueva cita: {nombre} reservó el {fecha} a las {hora}. Tel: {telefono}"

        enviar_correo(email, asunto, cuerpo_cliente)
        enviar_correo("Mocobarber032@gmail.com", asunto, cuerpo_barbero)

     

        return redirect("/confirmacion")
        
    # ↓↓↓ Este bloque es para cuando el usuario entra al formulario
    fecha_seleccionada = request.args.get("fecha")
    servicio_seleccionado = request.args.get("servicio")

    duracion = DURACIONES_SERVICIOS.get(servicio_seleccionado, 30)

    if not fecha_seleccionada:
        fecha_seleccionada = datetime.today().strftime("%Y-%m-%d")

    fecha_actual = datetime.today().strftime("%Y-%m-%d")  # ← Añadido
    fecha_maxima = (datetime.today() + timedelta(weeks=3)).strftime("%Y-%m-%d")
    reservas_fecha = Reserva.query.filter_by(fecha=fecha_seleccionada).all()
    horarios = obtener_horarios_disponibles(reservas_fecha, duracion)

    return render_template("citas.html", horarios=horarios, fecha=fecha_seleccionada, fecha_actual=fecha_actual, fecha_maxima=fecha_maxima, servicio=servicio_seleccionado)

@app.route("/confirmacion")
def confirmacion():
    return render_template("confirmacion.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/servicios")
def servicios():
    return render_template("servicios.html")

@app.route("/cancelar", methods=["GET", "POST"])
def cancelar():
    if request.method == "POST":
        telefono = request.form.get("telefono").strip()
        fecha = request.form.get("fecha")

        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return render_template("cancelar.html", mensaje="Fecha no válida.")
        
        # Buscar la reserva por telefono y fecha
        reserva = Reserva.query.filter_by(telefono=telefono, fecha=fecha).first()

        if not reserva:
           return render_template("cancelar.html", mensaje="No se encontró ninguna reserva con ese teléfono y fecha.")

        # Configuración de Google Calendar
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        CALENDAR_ID = 'Mocobarber032@gmail.com'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        calendar_service = build('calendar', 'v3', credentials=credentials)

        # Eliminar evento de Google Calendar si existe event_id
        if reserva.event_id:
            try:
                calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=reserva.event_id).execute()
            except Exception as e:
                print(f"Error al eliminar evento de Google Calendar: {e}")

        # Eliminar la reserva de la base de datos
        db.session.delete(reserva)
        db.session.commit()

        # Enviar correos
        asunto = "Tu cita ha sido cancelada ❌"
        cuerpo_cliente =f'''Hola {reserva.nombre} ,

He recibido la cancelación de tu cita en MocoBarber.

Para el {fecha} a las {reserva.hora}

Lamento que no podamos vernos esta vez, pero entiendo que a veces surgen imprevistos. 

Cuando estés listo para agendar de nuevo, estaré encantado de atenderte y dejarte impecable como siempre.

Puedes reservar tu próxima cita en cualquier momento desde web o escribiéndome directamente.

¡Hasta pronto!'''
        
        
        cuerpo_barbero = f"📅 Anulación cita: {reserva.nombre} canceló la cita para el {fecha} a las {reserva.hora}. Tel: {telefono}"

        enviar_correo(reserva.email, asunto, cuerpo_cliente)
        enviar_correo("Mocobarber032@gmail.com", asunto, cuerpo_barbero)




        return render_template("confirmar_cancel.html", mensaje="Reserva cancelada correctamente.")

    return render_template("cancelar.html")

#Utilizamos esta ruta para hacer un ping a la base de datos desde neon
#para que no se duerma la base de datos
@app.route("/db_ping")
def db_ping():
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        return "DB alive", 200
    except Exception as e:
        return f"DB error: {str(e)}", 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)