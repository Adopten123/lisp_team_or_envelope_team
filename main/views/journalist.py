from django.http import HttpResponse
from django.shortcuts import render
from ..models import NewsPost, Person, StudentRole

def journalist_news_view(request):
    """
    Функция для добавления новостей.
    Добавление новостей доступно для журналиста.
    """
    pass
