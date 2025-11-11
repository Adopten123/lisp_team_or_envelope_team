def get_person(user):
    return getattr(user, "person", None)

def get_role_code(user):
    person = get_person(user)
    role = getattr(person, "role", None) if person else None
    return getattr(role, "permission", None)

def moderator_level(code):
    if code == "Moderator_3lvl":
        return 3
    if code == "Moderator_2lvl":
        return 2
    if code == "Moderator_1lvl":
        return 1
    return 0

def is_moderator_min(user, min_level: int):
    return moderator_level(get_role_code(user)) >= min_level