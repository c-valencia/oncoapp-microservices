import os
from dotenv import load_dotenv

load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_URL", "https://oncoapp-239j.onrender.com")
PATIENT_SERVICE_URL = os.getenv("PATIENT_URL", "https://patientoncoassist.onrender.com")
RECOMMENDATION_SERVICE_URL = os.getenv("RECOMMENDATION_URL", "https://oncoai-4rec.onrender.com")