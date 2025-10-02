# main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="User CRUD + Controlled Brute Force Lab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserIn(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)  
    email: Optional[EmailStr] = None
    is_active: bool = True

class UserOut(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr] = None
    is_active: bool

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str
    password: str


_users: dict = {}

def _create_user_record(username: str, password: str, email: Optional[str], is_active: bool) -> dict:
    uid = str(uuid4())
    rec = {
        "id": uid,
        "username": username,
        "password": password,  
        "email": email,
        "is_active": is_active
    }
    _users[uid] = rec
    return rec


_create_user_record("admin4", "1234", "admin@example.com", True)
_create_user_record("testuser1", "passw0rd", "test@example.com", True)


def _find_by_username(username: str) -> Optional[dict]:
    for u in _users.values():
        if u["username"] == username:
            return u
    return None

def _ensure_unique_username(username: str, exclude_id: Optional[str] = None):
    for uid, u in _users.items():
        if u["username"] == username and uid != exclude_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserIn):
    _ensure_unique_username(payload.username)
    rec = _create_user_record(payload.username, payload.password, payload.email, payload.is_active)
    return UserOut(**rec)

@app.get("/users", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 100):
    users_list = list(_users.values())
    sliced = users_list[skip: skip + limit]
    return [UserOut(**u) for u in sliced]

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    rec = _users.get(user_id)
    if not rec:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**rec)

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdate):
    rec = _users.get(user_id)
    if not rec:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.username:
        _ensure_unique_username(payload.username, exclude_id=user_id)
        rec["username"] = payload.username
    if payload.email is not None:
        rec["email"] = payload.email
    if payload.is_active is not None:
        rec["is_active"] = payload.is_active
    _users[user_id] = rec
    return UserOut(**rec)

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    del _users[user_id]
    return {}


class PasswordChange(BaseModel):
    username: str
    old_password: str
    new_password: str

@app.post("/users/change-password")
def change_password(payload: PasswordChange):
    rec = _find_by_username(payload.username)
    if not rec:
        raise HTTPException(status_code=404, detail="User not found")
    if rec["password"] != payload.old_password:
        raise HTTPException(status_code=401, detail="Old password incorrect")
    rec["password"] = payload.new_password
    return {"message": "Password updated"}

@app.post("/login")
def login(payload: LoginRequest):
    rec = _find_by_username(payload.username)
    if not rec or rec["password"] != payload.password:
        # no detalles sobre si el usuario existe o no, solo login fallido
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not rec.get("is_active", True):
        raise HTTPException(status_code=403, detail="User inactive")
    return {"message": "Login successful", "user": rec["username"]}


@app.get("/")
def root():
    return {"message": "User CRUD + Brute Force Lab running. Check /docs for API UI."}
