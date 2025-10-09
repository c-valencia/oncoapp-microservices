from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import httpx
import os
from typing import Optional, List

router = APIRouter()
security = HTTPBearer(auto_error=False)

PATIENT_SERVICE_URL = os.getenv("PATIENT_URL", "https://patientoncoassist.onrender.com")

# ---------------------------
# 📁 MODELOS Pydantic
# ---------------------------

class PatientCreate(BaseModel):
    document_id: str
    name: str
    age: int
    gender: str
    race: Optional[str] = None
    region: Optional[str] = None
    urban_or_rural: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class PatientRead(PatientCreate):
    created: str
    edited: str

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    region: Optional[str] = None
    urban_or_rural: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ValidationError(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: list[ValidationError]

class ClinicalHistoryCreate(BaseModel):
    document_id: str
    stage_at_diagnosis: str
    tumor_aggressiveness: str
    treatment_access: str
    follow_up_adherence: str

class ClinicalHistoryRead(ClinicalHistoryCreate):
    id: int
    created: str
    edited: str

class ClinicalHistoryUpdate(BaseModel):
    stage_at_diagnosis: Optional[str] = None
    tumor_aggressiveness: Optional[str] = None
    treatment_access: Optional[str] = None
    follow_up_adherence: Optional[str] = None

# ---------------------------
# 📁 PACIENTES
# ---------------------------

@router.get("/patients/", response_model=List[PatientRead])
async def list_patients(
    page: Optional[int] = Query(None, title="Page"),
    page_size: Optional[int] = Query(None, title="Page Size"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    params = {}
    if page is not None:
        params["page"] = page
    if page_size is not None:
        params["page_size"] = page_size

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/patients/", params=params, headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.post("/patients/", response_model=PatientRead, status_code=201)
async def create_patient(
    patient: PatientCreate,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PATIENT_SERVICE_URL}/patients/", json=patient.dict(), headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.get("/patients/{document_id}", response_model=PatientRead)
async def get_patient(
    document_id: str = Path(..., title="Document Id"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/patients/{document_id}", headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.patch("/patients/{document_id}", response_model=PatientRead)
async def update_patient(
    document_id: str = Path(..., title="Document Id"),
    patient_update: PatientUpdate = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{PATIENT_SERVICE_URL}/patients/{document_id}", json=patient_update.dict(exclude_unset=True), headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.delete("/patients/{document_id}", status_code=204)
async def delete_patient(
    document_id: str = Path(..., title="Document Id"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PATIENT_SERVICE_URL}/patients/{document_id}", headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return None

# ---------------------------
# 📁 HISTORIALES CLÍNICOS
# ---------------------------

@router.post("/clinical_histories/", response_model=ClinicalHistoryRead, status_code=201)
async def create_clinical_history(
    clinical_history: ClinicalHistoryCreate,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PATIENT_SERVICE_URL}/clinical_histories/", json=clinical_history.dict(), headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.get("/clinical_histories/{history_id}", response_model=ClinicalHistoryRead)
async def get_clinical_history(
    history_id: int = Path(..., title="History Id"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/clinical_histories/{history_id}", headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.patch("/clinical_histories/{history_id}", response_model=ClinicalHistoryRead)
async def update_clinical_history(
    history_id: int = Path(..., title="History Id"),
    clinical_history_update: ClinicalHistoryUpdate = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{PATIENT_SERVICE_URL}/clinical_histories/{history_id}", json=clinical_history_update.dict(exclude_unset=True), headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.delete("/clinical_histories/{history_id}", status_code=204)
async def delete_clinical_history(
    history_id: int = Path(..., title="History Id"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{PATIENT_SERVICE_URL}/clinical_histories/{history_id}", headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return None

@router.get("/clinical_histories/document/{document_id}", response_model=List[ClinicalHistoryRead])
async def get_histories_by_document(
    document_id: str = Path(..., title="Document Id"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PATIENT_SERVICE_URL}/clinical_histories/document/{document_id}", headers={"authorization": f"Bearer {token.credentials}"} if token else {})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()