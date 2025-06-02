from pydantic import BaseModel

# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    nin: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    nin: str
    role: str

    class Config:
        orm_mode = True
