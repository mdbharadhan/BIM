def check_user_permission(role: str, page: str) -> bool:
    """RBAC guard logic."""
    if role == "Lead BIM Architect":
        return True
    if page in ["Dashboard", "Buildings", "BIM Models"]:
        return True
    return False