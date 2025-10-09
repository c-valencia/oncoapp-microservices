from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, patient_routes

app = FastAPI(
    title="OncoApp API Gateway",
    description="Gateway que orquesta los microservicios de OncoApp (Autenticación, Pacientes, etc.)",
    version="1.0.0"
)

# Permitir solicitudes desde tu frontend y otros orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia '*' por tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de los microservicios
app.include_router(auth_routes.router, prefix="/auth", tags=["Autenticación"])
app.include_router(patient_routes.router, prefix="/patients", tags=["Pacientes"])

@app.get("/")
def root():
    return {"message": "API Gateway de OncoApp funcionando correctamente 🚀"}