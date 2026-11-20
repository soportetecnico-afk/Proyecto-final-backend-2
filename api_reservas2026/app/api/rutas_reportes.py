from datetime import date
from typing import Optional
import csv
import io
import os
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.database import Database

router = APIRouter(prefix="/reportes", tags=["Reportes"])
db = Database()


class SolicitudCorreo(BaseModel):
    destinatario: str
    tipo_reporte: str = "reservas"
    fecha_inicial: Optional[date] = None
    fecha_final: Optional[date] = None
    estado_reserva: Optional[str] = None


@router.post("/enviar")
def enviar_reporte(solicitud: SolicitudCorreo):
    """Envía el detalle del reporte como CSV adjunto. Requiere SMTP configurado."""
    import re

    if solicitud.tipo_reporte not in {"reservas", "espacios", "recursos"}:
        raise HTTPException(status_code=422, detail="El tipo de reporte no es válido.")
    if solicitud.estado_reserva not in {None, "Pendiente", "Aprobada", "Rechazada", "Cancelada"}:
        raise HTTPException(status_code=422, detail="El estado de reserva no es válido.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", solicitud.destinatario):
        raise HTTPException(status_code=422, detail="El correo destinatario no es válido.")

    config = {
        "host": os.getenv("SMTP_HOST"),
        "user": os.getenv("SMTP_USER"),
        "password": (os.getenv("SMTP_PASSWORD") or "").replace(" ", ""),
        "sender": os.getenv("SMTP_FROM") or os.getenv("SMTP_USER"),
    }
    if not all(config.values()):
        raise HTTPException(
            status_code=503,
            detail="Configura SMTP_HOST, SMTP_USER, SMTP_PASSWORD y SMTP_FROM en el archivo .env para habilitar el envío.",
        )
    if solicitud.fecha_inicial and solicitud.fecha_final and solicitud.fecha_final < solicitud.fecha_inicial:
        raise HTTPException(status_code=400, detail="La fecha final no puede ser anterior a la fecha inicial.")

    datos = consultar_reportes(
        solicitud.tipo_reporte,
        solicitud.fecha_inicial,
        solicitud.fecha_final,
        solicitud.estado_reserva,
    )
    salida = io.StringIO()
    if datos["detalle"]:
        escritor = csv.DictWriter(salida, fieldnames=list(datos["detalle"][0].keys()))
        escritor.writeheader()
        escritor.writerows(datos["detalle"])
    else:
        salida.write("Sin registros para los criterios seleccionados.\n")

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Reporte de {solicitud.tipo_reporte} - Reservas CUL"
    mensaje["From"] = config["sender"]
    mensaje["To"] = solicitud.destinatario
    mensaje.set_content(
        f"Adjunto el reporte de {solicitud.tipo_reporte}. Registros: {datos['total_registros']}. "
        f"Fechas: {solicitud.fecha_inicial or 'sin inicio'} a {solicitud.fecha_final or 'sin fin'}."
    )
    mensaje.add_attachment(
        salida.getvalue().encode("utf-8-sig"),
        maintype="text",
        subtype="csv",
        filename=f"reporte-{solicitud.tipo_reporte}.csv",
    )

    try:
        with smtplib.SMTP(config["host"], int(os.getenv("SMTP_PORT", "587")), timeout=20) as servidor:
            servidor.starttls()
            servidor.login(config["user"], config["password"])
            servidor.send_message(mensaje)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"No fue posible enviar el correo mediante SMTP: {e}")
    return {"mensaje": "Reporte enviado", "destinatario": solicitud.destinatario}


@router.get("/tablero")
def consultar_tablero(
    fecha_inicial: Optional[date] = Query(None),
    fecha_final: Optional[date] = Query(None),
):
    """Vista pública de solo agregados para el iframe; no devuelve filas ni datos personales."""
    if fecha_inicial and fecha_final and fecha_final < fecha_inicial:
        raise HTTPException(status_code=400, detail="La fecha final no puede ser anterior a la inicial.")

    conn = db.get_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="No fue posible conectar con la base de datos.")

    try:
        condiciones = ["r.estado = TRUE"]
        params = []
        if fecha_inicial:
            condiciones.append("r.fecha_reserva >= %s")
            params.append(fecha_inicial)
        if fecha_final:
            condiciones.append("r.fecha_reserva <= %s")
            params.append(fecha_final)
        where = " AND ".join(condiciones)

        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT COUNT(*) AS total_reservas,
                       COUNT(DISTINCT r.id_espacio) AS espacios_utilizados,
                       COALESCE(SUM(r.cantidad_asistentes), 0) AS total_asistentes
                FROM reserva r WHERE {where}
            """, params)
            indicadores = cursor.fetchone()

            cursor.execute(f"""
                SELECT r.estado_reserva AS etiqueta, COUNT(*) AS total
                FROM reserva r WHERE {where}
                GROUP BY r.estado_reserva ORDER BY total DESC
            """, params)
            distribucion = cursor.fetchall()

            cursor.execute(f"""
                SELECT r.fecha_reserva AS fecha, COUNT(*) AS total
                FROM reserva r WHERE {where}
                GROUP BY r.fecha_reserva ORDER BY r.fecha_reserva
            """, params)
            serie = cursor.fetchall()

        return {"indicadores": indicadores, "distribucion": distribucion, "serie": serie}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar el tablero: {e}")
    finally:
        conn.close()


@router.get("/")
def consultar_reportes(
    tipo_reporte: str = Query("reservas", pattern="^(reservas|espacios|recursos)$"),
    fecha_inicial: Optional[date] = Query(None),
    fecha_final: Optional[date] = Query(None),
    estado_reserva: Optional[str] = Query(None),
):
    """Devuelve indicadores, distribución, serie temporal y detalle del reporte."""
    if fecha_inicial and fecha_final and fecha_final < fecha_inicial:
        raise HTTPException(
            status_code=400,
            detail="La fecha final no puede ser anterior a la fecha inicial.",
        )

    conn = db.get_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="No fue posible conectar con la base de datos.")

    try:
        with conn.cursor() as cursor:
            # Los filtros de fechas se aplican a las reservas. Para recursos, la
            # asignación no tiene fecha propia en el esquema actual.
            if tipo_reporte == "reservas":
                condiciones = ["r.estado = TRUE"]
                params = []
                if fecha_inicial:
                    condiciones.append("r.fecha_reserva >= %s")
                    params.append(fecha_inicial)
                if fecha_final:
                    condiciones.append("r.fecha_reserva <= %s")
                    params.append(fecha_final)
                if estado_reserva:
                    condiciones.append("r.estado_reserva = %s")
                    params.append(estado_reserva)
                where = " AND ".join(condiciones)

                cursor.execute(f"""
                    SELECT COUNT(*) AS total_reservas,
                           COUNT(DISTINCT r.id_espacio) AS espacios_utilizados,
                           COALESCE(SUM(r.cantidad_asistentes), 0) AS total_asistentes
                    FROM reserva r WHERE {where}
                """, params)
                indicadores = cursor.fetchone()

                cursor.execute(f"""
                    SELECT r.id_reserva, te.nombre_evento AS tipo,
                           e.nombre_espacio AS espacio, r.fecha_reserva,
                           r.hora_inicio, r.hora_fin, r.cantidad_asistentes,
                           r.estado_reserva AS estado,
                           u.nombre_completo AS usuario
                    FROM reserva r
                    JOIN espacio e ON e.id_espacio = r.id_espacio
                    JOIN tipo_evento te ON te.id_tipo_evento = r.id_tipo_evento
                    JOIN usuario u ON u.id_usuario = r.id_usuario
                    WHERE {where}
                    ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC, r.id_reserva DESC
                """, params)
                detalle = cursor.fetchall()

                cursor.execute(f"""
                    SELECT r.estado_reserva AS etiqueta, COUNT(*) AS total
                    FROM reserva r WHERE {where}
                    GROUP BY r.estado_reserva ORDER BY total DESC
                """, params)
                distribucion = cursor.fetchall()

                cursor.execute(f"""
                    SELECT r.fecha_reserva AS fecha, COUNT(*) AS total
                    FROM reserva r WHERE {where}
                    GROUP BY r.fecha_reserva ORDER BY r.fecha_reserva
                """, params)
                serie = cursor.fetchall()

                cursor.execute("SELECT COUNT(*) AS total FROM recurso WHERE estado = TRUE")
                total_recursos = cursor.fetchone()["total"]
                indicadores["total_recursos"] = total_recursos

            elif tipo_reporte == "espacios":
                condiciones = ["r.estado = TRUE", "e.estado = TRUE"]
                params = []
                if fecha_inicial:
                    condiciones.append("r.fecha_reserva >= %s")
                    params.append(fecha_inicial)
                if fecha_final:
                    condiciones.append("r.fecha_reserva <= %s")
                    params.append(fecha_final)
                where = " AND ".join(condiciones)

                cursor.execute("SELECT COUNT(*) AS total FROM espacio WHERE estado = TRUE")
                total_espacios = cursor.fetchone()["total"]
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT e.id_espacio) AS espacios_utilizados
                    FROM espacio e JOIN reserva r ON r.id_espacio = e.id_espacio
                    WHERE {where}
                """, params)
                usados = cursor.fetchone()["espacios_utilizados"]
                cursor.execute(f"""
                    SELECT COUNT(*) AS total_reservas FROM reserva r
                    JOIN espacio e ON e.id_espacio = r.id_espacio WHERE {where}
                """, params)
                total_reservas = cursor.fetchone()["total_reservas"]
                indicadores = {
                    "total_reservas": total_reservas,
                    "espacios_utilizados": usados,
                    "total_recursos": total_espacios,
                }
                cursor.execute(f"""
                    SELECT e.id_espacio, e.nombre_espacio AS espacio,
                           te.nombre_tipo AS tipo, e.ubicacion_piso,
                           COUNT(r.id_reserva) AS total_reservas,
                           COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva = 'Aprobada') AS aprobadas,
                           COUNT(r.id_reserva) FILTER (WHERE r.estado_reserva = 'Pendiente') AS pendientes,
                           e.estado
                    FROM espacio e
                    JOIN tipo_espacio te ON te.id_tipo_espacio = e.id_tipo_espacio
                    LEFT JOIN reserva r ON r.id_espacio = e.id_espacio
                        AND r.estado = TRUE
                        AND (%s::date IS NULL OR r.fecha_reserva >= %s)
                        AND (%s::date IS NULL OR r.fecha_reserva <= %s)
                    WHERE e.estado = TRUE
                    GROUP BY e.id_espacio, e.nombre_espacio, te.nombre_tipo, e.ubicacion_piso, e.estado
                    ORDER BY total_reservas DESC, e.nombre_espacio
                """, [fecha_inicial, fecha_inicial, fecha_final, fecha_final])
                detalle = cursor.fetchall()
                distribucion = [
                    {"etiqueta": "Con reservas", "total": usados},
                    {"etiqueta": "Sin reservas", "total": max(total_espacios - usados, 0)},
                ]
                cursor.execute(f"""
                    SELECT r.fecha_reserva AS fecha, COUNT(*) AS total
                    FROM reserva r JOIN espacio e ON e.id_espacio = r.id_espacio
                    WHERE {where} GROUP BY r.fecha_reserva ORDER BY r.fecha_reserva
                """, params)
                serie = cursor.fetchall()

            else:  # recursos
                cursor.execute("""
                    SELECT COUNT(*) AS total_recursos,
                           COALESCE(SUM(er.cantidad_asignada), 0) AS unidades_asignadas,
                           COUNT(DISTINCT er.id_espacio) AS espacios_con_recursos
                    FROM recurso re
                    LEFT JOIN espacio_recurso er ON er.id_recurso = re.id_recurso AND er.estado = TRUE
                    WHERE re.estado = TRUE
                """)
                resumen = cursor.fetchone()
                indicadores = {
                    "total_reservas": resumen["unidades_asignadas"],
                    "espacios_utilizados": resumen["espacios_con_recursos"],
                    "total_recursos": resumen["total_recursos"],
                }
                cursor.execute("""
                    SELECT re.id_recurso, re.nombre_recurso AS recurso,
                           re.categoria, re.estado_mantenimiento,
                           COALESCE(SUM(er.cantidad_asignada), 0) AS cantidad_asignada,
                           COUNT(DISTINCT er.id_espacio) AS espacios_asignados,
                           re.estado
                    FROM recurso re
                    LEFT JOIN espacio_recurso er ON er.id_recurso = re.id_recurso AND er.estado = TRUE
                    WHERE re.estado = TRUE
                    GROUP BY re.id_recurso, re.nombre_recurso, re.categoria,
                             re.estado_mantenimiento, re.estado
                    ORDER BY re.nombre_recurso
                """)
                detalle = cursor.fetchall()
                cursor.execute("""
                    SELECT re.estado_mantenimiento AS etiqueta, COUNT(*) AS total
                    FROM recurso re WHERE re.estado = TRUE
                    GROUP BY re.estado_mantenimiento ORDER BY total DESC
                """)
                distribucion = cursor.fetchall()
                cursor.execute("""
                    SELECT e.nombre_espacio AS etiqueta, SUM(er.cantidad_asignada) AS total
                    FROM espacio_recurso er
                    JOIN espacio e ON e.id_espacio = er.id_espacio AND e.estado = TRUE
                    JOIN recurso re ON re.id_recurso = er.id_recurso AND re.estado = TRUE
                    WHERE er.estado = TRUE
                    GROUP BY e.id_espacio, e.nombre_espacio
                    ORDER BY total DESC, e.nombre_espacio
                """)
                serie = cursor.fetchall()

        return {
            "tipo_reporte": tipo_reporte,
            "fecha_inicial": fecha_inicial,
            "fecha_final": fecha_final,
            "indicadores": indicadores,
            "distribucion": distribucion,
            "serie": serie,
            "detalle": detalle,
            "total_registros": len(detalle),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar reportes: {str(e)}")
    finally:
        conn.close()
