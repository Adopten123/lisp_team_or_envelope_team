from django.http import HttpResponse

def headman_group_news_view(request):
    return HttpResponse("Страница создания и просмотра существующих новостей")