"""RBAC: authentication (who are you) is trimmed to a header for this
lesson's scope — C-1 already teaches real JWT auth. What belongs HERE is
authorization: require_manager is a dependency FACTORY that 403s anyone
whose role claim isn't MANAGER, independent of how that role was proven.
"""
from fastapi import Header, HTTPException, status

from app.schemas import Role


def get_current_role(x_user_role: Role = Header(...)) -> Role:
    return x_user_role


def get_current_user_id(x_user_id: int = Header(...)) -> int:
    return x_user_id


def require_manager(x_user_role: Role = Header(...)) -> Role:
    if x_user_role != "MANAGER":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Manager role required")
    return x_user_role
