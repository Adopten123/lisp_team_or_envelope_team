from django.http import HttpResponse

"""
Пока что не трогать то, что ниже
"""

def acts_view(request):
    return HttpResponse("Страница просмотра актов университета")

def news_moderation(request, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def group_news_moderation(request, group_slug, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def student_admin_list(request):
    return HttpResponse("Страница взаимодействия со студентами")