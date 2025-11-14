from django.http import HttpResponse
from main.utils.placeholder import render_under_development

"""
Пока что не трогать то, что ниже
"""

def acts_view(request):
    """
    Страница актов
    """
    return render_under_development(
        request,
        title="🛠️ Функционал просмотра актов",
        message="Скоро здесь появится полный функционал просмотра актов.",
        additional_info="Вы сможете просматривать акты."
    )

def news_moderation(request, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def group_news_moderation(request, group_slug, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def student_admin_list(request):
    return HttpResponse("Страница взаимодействия со студентами")