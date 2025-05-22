from config import HORARIOS_DISPONIBLES, DURACIONES_SERVICIOS
import math

def obtener_horarios_disponibles(reservas, duracion_minutos=30):
    ocupados = set()

    # 1. Marcar bloques ocupados según duración de cada reserva
    for r in reservas:
        duracion_reserva = DURACIONES_SERVICIOS.get(r.servicio, 30)
        bloques_reserva = math.ceil(duracion_reserva / 30)
        if r.hora in HORARIOS_DISPONIBLES:
            i = HORARIOS_DISPONIBLES.index(r.hora)
            for b in range(bloques_reserva):
                if i + b < len(HORARIOS_DISPONIBLES):
                    ocupados.add(HORARIOS_DISPONIBLES[i + b])

    # 2. Buscar bloques disponibles para nueva reserva
    disponibles = []
    bloques_necesarios = math.ceil(duracion_minutos / 30)

    for i in range(len(HORARIOS_DISPONIBLES) - bloques_necesarios + 1):
        bloque = HORARIOS_DISPONIBLES[i:i + bloques_necesarios]
        if all(h not in ocupados for h in bloque):
            disponibles.append(HORARIOS_DISPONIBLES[i])

    return disponibles