from django.http import HttpResponse
from django.shortcuts import render

def journalist_news_view(request):
    """
    Функция для добавления новостей.
    Добавление новостей доступно для журналиста.
    """

    return render(request, 'main/journalist/news_create.html')
