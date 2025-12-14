from pydantic import BaseModel

class EcommerceCreate(BaseModel):
    name: str