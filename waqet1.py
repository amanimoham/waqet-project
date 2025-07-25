from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from passlib.context import CryptContext
import uuid

app = FastAPI(title="WAQET Backend Prototype", version="1.0")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SignupRequest(BaseModel):
    name: str
    birthdate: str
    national_id: str
    organization: str
    job_title: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    name: str
    birthdate: str
    national_id: str
    organization: str
    job_title: str
    email: str

class FlightStatus(BaseModel):
    flight_number: str
    origin: str
    gate: str
    gpu_activated: bool

class ActivateGPURequest(BaseModel):
    flight_number: str
    gate: str

class PredictETARequest(BaseModel):
    distance_km: float
    speed_kmh: float

class EmissionRequest(BaseModel):
    apu_hours: float
    gpu_hours: float

users_db = []
sessions = {}
airports_data = {
    "RUH": ["Gate A1", "Gate A2", "Gate A3"],
    "JED": ["Gate B1", "Gate B2"],
    "DMM": ["Gate C1"]
}
flights_data = [
    {"flight_number": "XY101", "origin": "JED", "gate": "Gate A1", "gpu_activated": False},
    {"flight_number": "XY202", "origin": "DMM", "gate": "Gate A2", "gpu_activated": True},
]

notifications = [
    {"message": "فعل النظام للرحلة XY101 في البوابة Gate A1"},
    {"message": "فعل النظام للرحلة XY202 في البوابة Gate A2"}
]

def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return sessions[token]

@app.post("/auth/signup")
def signup(data: SignupRequest):
    for user in users_db:
        if user["email"] == data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    new_user = data.dict()
    new_user["id"] = str(uuid.uuid4())
    new_user["password"] = pwd_context.hash(data.password)
    users_db.append(new_user)
    return {"message": "User created successfully", "user_id": new_user["id"]}

@app.post("/auth/login")
def login(data: LoginRequest):
    for user in users_db:
        if user["email"] == data.email and pwd_context.verify(data.password, user_
