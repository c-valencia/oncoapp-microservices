from fastapi import APIRouter, Request, HTTPException, Depends
import httpx
import os

router = APIRouter()
AUTH_SERVICE_URL = os.getenv("AUTH_URL", "https://oncoapp-239j.onrender.com")


async def forward_request(method: str, endpoint: str, request: Request, requires_auth: bool = False):
    """
    Helper para reenviar peticiones al microservicio de autenticación.
    """
    headers = dict(request.headers)
    if requires_auth:
        if "authorization" not in headers:
            raise HTTPException(status_code=401, detail="Token de autorización faltante")

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(f"{AUTH_SERVICE_URL}{endpoint}", headers=headers, params=request.query_params)
            elif method == "POST":
                data = await request.json()
                response = await client.post(f"{AUTH_SERVICE_URL}{endpoint}", headers=headers, json=data)
            elif method == "PUT":
                data = await request.json()
                response = await client.put(f"{AUTH_SERVICE_URL}{endpoint}", headers=headers, json=data)
            else:
                raise HTTPException(status_code=405, detail="Método no permitido")

            return response
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error al contactar el servicio de autenticación: {e}")


def handle_response(response: httpx.Response):
    """Procesa la respuesta HTTP estándar."""
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    try:
        return response.json()
    except Exception:
        return {"message": response.text}


# ---------------------------
# 🔐 Rutas públicas
# ---------------------------

@router.post("/register")
async def register(request: Request):
    """
    Registrar un nuevo usuario/médico.
    """
    response = await forward_request("POST", "/register", request)
    return handle_response(response)


@router.post("/login")
async def login(request: Request):
    """
    Iniciar sesión y obtener token de acceso.
    """
    response = await forward_request("POST", "/login", request)
    return handle_response(response)


# ---------------------------
# 👤 Rutas autenticadas
# ---------------------------

@router.get("/me")
async def get_me(request: Request):
    """
    Obtener información del usuario autenticado.
    """
    response = await forward_request("GET", "/me", request, requires_auth=True)
    return handle_response(response)


# ---------------------------
# 🧑‍⚕️ Rutas de administración
# ---------------------------

@router.get("/admin/users")
async def list_users(request: Request):
    response = await forward_request("GET", "/admin/users", request, requires_auth=True)
    return handle_response(response)


@router.get("/admin/medicos")
async def list_medicos(request: Request):
    response = await forward_request("GET", "/admin/medicos", request, requires_auth=True)
    return handle_response(response)


@router.get("/admin/user-medico/{user_id}")
async def get_user_medico(user_id: str, request: Request):
    response = await forward_request("GET", f"/admin/user-medico/{user_id}", request, requires_auth=True)
    return handle_response(response)


@router.put("/admin/user-medico/{user_id}")
async def update_user_medico(user_id: str, request: Request):
    response = await forward_request("PUT", f"/admin/user-medico/{user_id}", request, requires_auth=True)
    return handle_response(response)


# ---------------------------
# 🔍 Búsquedas
# ---------------------------

@router.get("/search")
async def search_user_medico(request: Request):
    response = await forward_request("GET", "/search", request, requires_auth=True)
    return handle_response(response)


@router.get("/search/flexible")
async def search_flexible(request: Request):
    response = await forward_request("GET", "/search/flexible", request, requires_auth=True)
    return handle_response(response)
