from pydantic import BaseModel

class AgencyCreate(BaseModel):
    agency_name: str
    agency_email: str
    admin_name: str
    admin_email: str
    admin_password: str
    is_active: bool = True
