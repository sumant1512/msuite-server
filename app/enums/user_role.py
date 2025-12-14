from enum import Enum

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    AGENCY_ADMIN = "AGENCY_ADMIN"
    ECOMMERCE_USER = "ECOMMERCE_USER"
