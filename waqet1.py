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
        if user["email"] == data.email and pwd_context.verify(data.password, user["password"]):
            token = str(uuid.uuid4())
            sessions[token] = user
            return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/auth/profile", response_model=UserProfile)
def profile(user=Depends(get_current_user)):
    return user

@app.get("/airports/list")
def list_airports():
    return {"airports": list(airports_data.keys())}

@app.get("/airports/{airport_id}/gates")
def gates(airport_id: str):
    if airport_id not in airports_data:
        raise HTTPException(status_code=404, detail="Airport not found")
    return {"airport": airport_id, "gates": airports_data[airport_id]}

@app.get("/flights/timeline", response_model=List[FlightStatus])
def flight_timeline():
    return flights_data

@app.get("/flights/{gate_id}/status")
def gate_status(gate_id: str):
    gate_flights = [f for f in flights_data if f["gate"] == gate_id]
    return {"gate": gate_id, "flights": gate_flights}

@app.post("/flights/activate_gpu")
def activate_gpu(req: ActivateGPURequest):
    for flight in flights_data:
        if flight["flight_number"] == req.flight_number and flight["gate"] == req.gate:
            flight["gpu_activated"] = True
            return {"message": f"GPU Activated for {req.flight_number} at {req.gate}"}
    raise HTTPException(status_code=404, detail="Flight not found")

@app.get("/notifications/technician")
def technician_notifications():
    return {"notifications": notifications}

@app.post("/ai/predict_eta")
def predict_eta(req: PredictETARequest):
    if req.speed_kmh == 0:
        raise HTTPException(status_code=400, detail="Speed cannot be zero")
    eta = req.distance_km / req.speed_kmh
    return {"eta_hours": round(eta, 2)}

@app.post("/ai/emission_stats")
def emission_stats(req: EmissionRequest):
    apu_emission = req.apu_hours * 200 * 3.16
    gpu_emission = req.gpu_hours * 50 * 3.16
    saved = apu_emission - gpu_emission
    return {"apu_emission": apu_emission, "gpu_emission": gpu_emission, "saved_emission": saved}

@app.get("/dashboard/daily_reports")
def daily_reports():
    return {
        "total_flights": len(flights_data),
        "notifications_sent": len(notifications),
        "gpu_activated": sum(1 for f in flights_data if f["gpu_activated"])
    }

@app.get("/dashboard/sustainability")
def sustainability():
    saved_co2 = 500
    saved_fuel = 300
    return {"co2_saved": saved_co2, "fuel_saved": saved_fuel}

@app.get("/admin/panel")
def admin_panel(user=Depends(get_current_user)):
    if user["job_title"].lower() != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"users": users_db, "flights": flights_data}

@app.get("/static/about")
def about():
    return {"about": "WAQET - Smart Airport Sustainability System"}

@app.get("/static/contact")
def contact():
    return {"contact": "Contact us at info@waqet.com"}

@app.get("/static/privacy")
def privacy():
    return {"privacy": "We respect user privacy and data security."}

if __name__ == "__main__":
    print("App file loaded correctly")
