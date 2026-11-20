import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Literal, Optional
from app.models.reserva import Reserva
from app.repositories.reserva_repo import ReservaRepository
from app.core.auth import obtener_usuario_actual

router = APIRouter(prefix="/reservas", tags=["Gestión de Reservas"])
logger = logging.getLogger(__name__)
repo = ReservaRepository()


class DecisionReserva(BaseModel):
    decision: Literal["Confirmada", "Rechazada"]
    motivo_rechazo: Optional[str] = None


def exigir_administrador_o_decano(usuario_actual: dict):
    if int(usuario_actual["id_rol"]) not in (1, 3):
        raise HTTPException(status_code=403, detail="Tu perfil no tiene permiso para realizar esta acción.")


@router.get("/")
def listar_reservas(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Docente: solo sus reservas. Administrador y Decano: listado general."""
    try:
        return repo.obtener_todas(usuario_actual)
    except Exception:
        raise HTTPException(status_code=500, detail="No fue posible consultar las reservas.")


@router.get("/{reserva_id}")
def obtener_reserva(reserva_id: int, usuario_actual: dict = Depends(obtener_usuario_actual)):
    try:
        reserva = repo.obtener_por_id(reserva_id, usuario_actual)
        if not reserva:
            # 404 evita revelar si la reserva existe pero pertenece a otra persona.
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return reserva
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="No fue posible consultar la reserva.")


@router.post("/")
def crear_reserva(reserva: Reserva, usuario_actual: dict = Depends(obtener_usuario_actual)):
    # Los tres perfiles oficiales pueden solicitar reservas.
    # El solicitante se toma SIEMPRE del token, nunca del dato enviado por el frontend.
    if int(usuario_actual["id_rol"]) not in (1, 3, 5):
        raise HTTPException(status_code=403, detail="Tu perfil no tiene permiso para crear reservas.")
    # Validación autoritativa en backend: nunca confiar solo en el límite del frontend.
    try:
        espacio = repo.obtener_capacidad_espacio(int(reserva.id_espacio))
    except Exception as e:
        logger.exception("Error al consultar el aforo del espacio %s", reserva.id_espacio)
        raise HTTPException(status_code=500, detail="No fue posible verificar la capacidad del espacio.") from e

    if not espacio:
        raise HTTPException(status_code=404, detail="El espacio seleccionado no existe o no está disponible.")

    capacidad_maxima = int(espacio["capacidad_aforo"])
    cantidad_solicitada = int(reserva.cantidad_asistentes)
    if cantidad_solicitada > capacidad_maxima:
        nombre_espacio = espacio["nombre_espacio"]
        raise HTTPException(
            status_code=422,
            detail=(
                f"No es posible crear la reserva: la cantidad de asistentes ({cantidad_solicitada}) "
                f"supera la capacidad permitida de «{nombre_espacio}» ({capacidad_maxima} personas)."
            ),
        )

    try:
        reserva.id_usuario = int(usuario_actual["id_usuario"])
        reserva.estado_reserva = "Pendiente"
        reserva.id_aprobador = None
        nuevo_id = repo.crear(reserva)
        return {
            "mensaje": "Reserva creada exitosamente y enviada para aprobación.",
            "id_reserva": nuevo_id,
            "estado_reserva": "Pendiente",
        }
    except Exception as e:
        logger.exception("Error al crear reserva")
        raise HTTPException(status_code=400, detail=f"No fue posible crear la reserva: {e}")


@router.put("/{reserva_id}")
def actualizar_reserva(reserva_id: int, reserva: Reserva, usuario_actual: dict = Depends(obtener_usuario_actual)):
    exigir_administrador_o_decano(usuario_actual)
    try:
        exito = repo.actualizar(reserva_id, reserva)
        if not exito:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return {"mensaje": "Reserva actualizada correctamente"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="No fue posible actualizar la reserva.")


@router.delete("/{reserva_id}")
def eliminar_reserva(reserva_id: int, usuario_actual: dict = Depends(obtener_usuario_actual)):
    exigir_administrador_o_decano(usuario_actual)
    try:
        exito = repo.eliminar(reserva_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return {"mensaje": "Reserva eliminada correctamente"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="No fue posible eliminar la reserva.")


@router.patch("/{reserva_id}/decision")
def decidir_reserva(
    reserva_id: int,
    datos: DecisionReserva,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """Administrador y Decano pueden aprobar o rechazar una solicitud pendiente."""
    exigir_administrador_o_decano(usuario_actual)

    motivo = (datos.motivo_rechazo or "").strip()
    if datos.decision == "Rechazada" and not motivo:
        raise HTTPException(status_code=422, detail="Debes indicar el motivo del rechazo.")
    if datos.decision == "Confirmada":
        motivo = None

    try:
        actualizado = repo.resolver_decision(
            reserva_id=reserva_id,
            id_administrador=int(usuario_actual["id_usuario"]),
            decision=datos.decision,
            motivo_rechazo=motivo,
        )
        if not actualizado:
            raise HTTPException(
                status_code=409,
                detail="La reserva no existe, está inactiva o ya fue gestionada.",
            )
        return {
            "mensaje": "Reserva aprobada correctamente." if datos.decision == "Confirmada" else "Reserva rechazada. El motivo quedó registrado.",
            "id_reserva": reserva_id,
            "estado_reserva": datos.decision,
            "motivo_rechazo": motivo,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error al registrar decisión de la reserva %s", reserva_id)
        raise HTTPException(
            status_code=500,
            detail="No fue posible registrar la decisión. Revisa la terminal de FastAPI para ver el error SQL.",
        ) from e
