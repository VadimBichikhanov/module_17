from pydantic import BaseModel
class CreateTask(BaseModel):
    title: str 
    content: str
    priority: int
    user_id: int 


class UpdateTask(BaseModel):
    title: str 
    content: str
    priority: int

