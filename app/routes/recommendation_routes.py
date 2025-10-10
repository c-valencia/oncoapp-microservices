from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
import os

router = APIRouter()
security = HTTPBearer(auto_error=False)

# URL del microservicio de predicción
RECOMMENDATION_SERVICE_URL = os.getenv(
    "RECOMMENDATION_URL",
    "https://oncoai-4rec.onrender.com"
)

# ---------------------------
# 📁 MODELOS Pydantic
# ---------------------------

class HistoryIdRequest(BaseModel):
    history_id: int

class TreatmentResponse(BaseModel):
    history_id: int
    treatment: str
    success: bool
    message: str

class ValidationError(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: list[ValidationError]

# ---------------------------
# 📁 ENDPOINTS
# ---------------------------

@router.get("/")
async def root():
    """
    Root del microservicio de recomendación.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{RECOMMENDATION_SERVICE_URL}/")
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error de conexión: {str(e)}")
    return response.json()


@router.get("/health")
async def health_check():
    """
    Verificación de salud del microservicio.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{RECOMMENDATION_SERVICE_URL}/health")
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error de conexión: {str(e)}")
    return response.json()


@router.post(
    "/api/v1/predict-and-update",
    response_model=TreatmentResponse,
    responses={
        422: {"model": HTTPValidationError}
    },
    tags=["prediction"],
    summary="Predict And Update Treatment",
    description="Predecir tratamiento y actualizar en Oncoassist.\nFlujo: GET historia → Extraer datos → Predecir → PATCH"
)
async def predict_and_update_treatment(
    request_data: HistoryIdRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint principal de predicción y actualización de tratamiento.
    """
    headers = {"Authorization": f"Bearer {token.credentials}"} if token else {}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{RECOMMENDATION_SERVICE_URL}/api/v1/predict-and-update",
                json=request_data.dict(),
                headers=headers
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error al conectar con el servicio de predicción: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
