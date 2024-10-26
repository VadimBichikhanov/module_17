from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int
    slug: str
    
    
class UpdateUser(BaseModel):
    firstname: str
    lastname: str
    age: int