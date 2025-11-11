from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def page_url(context, request, page_number):
    """
    Возвращает URL с теми же GET-параметрами:
    Пример: {% page_url request 3 %}
    """
    params = request.GET.copy()
    params["page"] = page_number
    qs = params.urlencode()
    return f"?{qs}" if qs else f"?page={page_number}"