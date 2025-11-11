from django.http import HttpResponse

def journalist_news_view(request):
    return HttpResponse("Страница создания новостей журналистами")