import os
raw = os.getenv("ROLES_BLOCKED_ALL_FUNCTIONS")

if not raw:
    raise ValueError("ROLES_BLOCKED_ALL_FUNCTIONS environment variable is not set.")

RESTRICTED_ROLES_GLOBAL = {
    item.strip().upper()
    for item in raw.split(",") 
    if item.strip()
}

def is_globally_restricted(roles_list: list[str]) -> bool:
    if not roles_list:
        return False
    user_roles = {r.strip().upper() for r in roles_list}
    return all(r in RESTRICTED_ROLES_GLOBAL for r in user_roles)
