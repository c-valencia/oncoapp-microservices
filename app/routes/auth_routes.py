from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import httpx
import os

router = APIRouter()
AUTH_SERVICE_URL = os.getenv("AUTH_URL", "https://oncoapp-239j.onrender.com")
security = HTTPBearer(auto_error=False)

# ---------------------------
# 🔐 Schemas Pydantic
# ---------------------------

class RegisterIn(BaseModel):
    email: str
    password: str
    nombres: str
    apellidos: str
    tipo_doc: str
    doc: str
    especialidades: str

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: str
    rol_id: int
    created_at: str

class MedicoOut(BaseModel):
    id: int
    user_id: str
    nombres: str
    apellidos: str
    tipo_doc: str
    doc: str
    especialidades: str
    created_at: str

class UserMedicoUpdateIn(BaseModel):
    email: str | None = None
    rol_id: int | None = None
    password: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    tipo_doc: str | None = None
    doc: str | None = None
    especialidades: str | None = None

class UserMedicoUpdateOut(BaseModel):
    usuario: UserOut
    medico: MedicoOut

class SearchResult(BaseModel):
    usuario: UserOut
    medico: MedicoOut
    encontrado_por: str

class ValidationError(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: list[ValidationError]

# ---------------------------
# 🔧 Helper para reenviar requests
# ---------------------------

async def forward_request(
    method: str,
    endpoint: str,
    request: Request,
    requires_auth: bool = False,
    json_data: dict = None,
    params: dict = None,
    token: HTTPAuthorizationCredentials | None = None
):
    headers = dict(request.headers)
    if requires_auth:
        if not token:
            raise HTTPException(status_code=401, detail="Token de autorización faltante")
        headers["authorization"] = f"Bearer {token.credentials}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                return await client.get(f"{AUTH_SERVICE_URL}{endpoint}", headers=headers, params=params or request.query_params)
            elif method == "POST":
                data = json_data or await request.json()
                return await client.post(f"{AUTH_SERVICE_URL}{endpoint}", headers=headers, json=data)
            elif method == "PUT":
                data = json_data or await request.json()
                return await client.put(f"{AUTH_SERVICE_URL}{endpoint}", headers=headers, json=data)
            else:
                raise HTTPException(status_code=405, detail="Método no permitido")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error al contactar el servicio de autenticación: {e}")

def handle_response(response: httpx.Response):
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    try:
        return response.json()
    except Exception:
        return {"message": response.text}

# ---------------------------
# 🔄 Manejo de errores de validación
# ---------------------------

@router.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [ValidationError(loc=e["loc"], msg=e["msg"], type=e["type"]) for e in exc.errors()]
    return JSONResponse(status_code=422, content=HTTPValidationError(detail=errors).dict())

# ---------------------------
# 🔐 Rutas públicas
# ---------------------------

@router.post("/register", status_code=201, response_model=dict)
async def register(request: Request):
    body = await request.json()
    validated = RegisterIn(**body)
    response = await forward_request("POST", "/register", request, json_data=validated.dict())
    return handle_response(response)

@router.post("/login", response_model=TokenOut)
async def login(request: Request):
    body = await request.json()
    validated = LoginIn(**body)
    response = await forward_request("POST", "/login", request, json_data=validated.dict())
    return handle_response(response)

# ---------------------------
# 👤 Rutas autenticadas
# ---------------------------

@router.get("/me", response_model=UserOut)
async def get_me(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    response = await forward_request("GET", "/me", request, requires_auth=True, token=token)
    return handle_response(response)

# ---------------------------
# 🧑‍⚕️ Rutas de administración
# ---------------------------

@router.get("/admin/users", response_model=list[UserOut])
async def list_users(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    response = await forward_request("GET", "/admin/users", request, requires_auth=True, token=token)
    return handle_response(response)

@router.get("/admin/medicos", response_model=list[MedicoOut])
async def list_medicos(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    response = await forward_request("GET", "/admin/medicos", request, requires_auth=True, token=token)
    return handle_response(response)

@router.get("/admin/user-medico/{user_id}", response_model=UserMedicoUpdateOut)
async def get_user_medico(user_id: str, request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    response = await forward_request("GET", f"/admin/user-medico/{user_id}", request, requires_auth=True, token=token)
    return handle_response(response)

@router.put("/admin/user-medico/{user_id}", response_model=UserMedicoUpdateOut)
async def update_user_medico(user_id: str, request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    body = await request.json()
    validated = UserMedicoUpdateIn(**body)
    response = await forward_request("PUT", f"/admin/user-medico/{user_id}", request, requires_auth=True, json_data=validated.dict(), token=token)
    return handle_response(response)

# ---------------------------
# 🔍 Búsquedas
# ---------------------------

@router.get("/search", response_model=SearchResult)
async def search_user_medico(
    request: Request,
    email: str | None = Query(default=None),
    tipo_doc: str | None = Query(default=None),
    doc: str | None = Query(default=None),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    params = {"email": email, "tipo_doc": tipo_doc, "doc": doc}
    response = await forward_request("GET", "/search", request, requires_auth=True, params=params, token=token)
    return handle_response(response)

@router.get("/search/flexible", response_model=list[SearchResult])
async def search_flexible(
    request: Request,
    q: str = Query(..., description="Término de búsqueda obligatorio"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    params = {"q": q}
    response = await forward_request("GET", "/search/flexible", request, requires_auth=True, params=params, token=token)
    return handle_response(response)
