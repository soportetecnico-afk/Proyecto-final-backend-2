from fastapi import APIRouter, HTTPException
from app.models.check_in import CheckIn
from app.repositories.check_in_repo import CheckInRepository

router = APIRouter(prefix="/check-ins", tags=["Gestión de Check-In"])
repo = CheckInRepository()

@router.get("/")
def listar_check_ins():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reserva/{reserva_id}")
def obtener_check_in_de_reserva(reserva_id: int):
    try:
        check_in = repo.obtener_por_reserva(reserva_id)
        if not check_in:
            raise HTTPException(status_code=404, detail="La reserva no registra check-in")
        return check_in
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{check_in_id}")
def obtener_check_in(check_in_id: int):
    try:
        check_in = repo.obtener_por_id(check_in_id)
        if not check_in:
            raise HTTPException(status_code=404, detail="Check-in no encontrado")
        return check_in
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_check_in(check_in: CheckIn):
    try:
        nuevo_id = repo.crear(check_in)
        return {"mensaje": "Check-in creado exitosamente", "id_check_in": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{check_in_id}")
def actualizar_check_in(check_in_id: int, check_in: CheckIn):
    try:
        exito = repo.actualizar(check_in_id, check_in)
        if not exito:
            raise HTTPException(status_code=404, detail="Check-in no encontrado")
        return {"mensaje": "Check-in actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{check_in_id}")
def eliminar_check_in(check_in_id: int):
    try:
        exito = repo.eliminar(check_in_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Check-in no encontrado")
        return {"mensaje": "Check-in eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))