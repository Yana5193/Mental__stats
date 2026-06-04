from pydantic import BaseModel

class LoginRequest(BaseModel):
    full_name: str
    password: str
    
class LoginResponse(BaseModel):
    emp_id: int
    full_name: str
    role: str

