from fastapi import APIRouter, HTTPException, Request
import httpx
import os

router = APIRouter(tags=["Patients", "Clinical Histories"])

PATIENT_SERVICE_URL = os.getenv("PATIENT_URL", "https://patientoncoassist.onrender.com")

# ============================
# 📁 PACIENTES
# ============================

# 🔹 Listar pacientes (paginación opcional)
@router.get("/patients/")
async def list_patients(page: int = None, page_size: int = None):
    params = {}
    if page is not None:
        params["page"] = page
    if page_size is not None:
        params["page_size"] = page_size

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/patients", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Crear paciente
@router.post("/patients/")
async def create_patient(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PATIENT_SERVICE_URL}/patients", json=data)
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Obtener paciente por document_id
@router.get("/patients/{document_id}")
async def get_patient(document_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/patients/{document_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Actualizar parcialmente paciente por document_id
@router.patch("/patients/{document_id}")
async def update_patient(document_id: str, request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{PATIENT_SERVICE_URL}/patients/{document_id}", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Eliminar paciente por document_id
@router.delete("/patients/{document_id}")
async def delete_patient(document_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PATIENT_SERVICE_URL}/patients/{document_id}")
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"message": "Patient deleted successfully"}


# ============================
# 📁 HISTORIALES CLÍNICOS
# ============================

# 🔹 Crear historial clínico
@router.post("/clinical_histories/")
async def create_clinical_history(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PATIENT_SERVICE_URL}/clinical_histories", json=data)
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Obtener historial clínico por history_id
@router.get("/clinical_histories/{history_id}")
async def get_clinical_history(history_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/clinical_histories/{history_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Actualizar parcialmente historial clínico
@router.patch("/clinical_histories/{history_id}")
async def update_clinical_history(history_id: int, request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{PATIENT_SERVICE_URL}/clinical_histories/{history_id}", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# 🔹 Eliminar historial clínico
@router.delete("/clinical_histories/{history_id}")
async def delete_clinical_history(history_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PATIENT_SERVICE_URL}/clinical_histories/{history_id}")
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"message": "Clinical history deleted successfully"}


# 🔹 Obtener historiales clínicos por document_id
@router.get("/clinical_histories/document/{document_id}")
async def get_histories_by_document(document_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/clinical_histories/document/{document_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
