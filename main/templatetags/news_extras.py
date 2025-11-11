from django import template

register = template.Library()

@register.filter
def news_icon(title: str):
    """Выбираем эмодзи по ключевым словам заголовка."""
    if not title:
        return "📰"
    t = title.lower()
    if any(k in t for k in ("лекция", "пара", "расписание", "занятие")):
        return "📚"
    if any(k in t for k in ("экзам", "зачет", "зачёт", "контроль")):
        return "📝"
    if any(k in t for k in ("мероприят", "день открытых", "концерт", "митап", "встреча")):
        return "🎉"
    if any(k in t for k in ("важно", "срочно", "внимание", "объявление")):
        return "🔔"
    return "📰"