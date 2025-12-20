import enum


class UserRole(enum.Enum):
    """User role enumeration for multi-tenant access control"""
    SUPER_ADMIN = "SUPER_ADMIN"
    AGENCY_ADMIN = "AGENCY_ADMIN"
    ECOMMERCE = "ECOMMERCE"
