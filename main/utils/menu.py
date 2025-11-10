from main.utils.buttons import buttons

def get_menu_buttons(role: str) -> list[dict]:
    return [btn for btn in buttons if role in btn["roles"]]