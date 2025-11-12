from django.http import HttpResponse
from django.shortcuts import render
from ..models import NewsPost, Person, StudentRole


def journalist_news_view(request):
    """
    Функция для добавления новостей.
    Добавление новостей доступно для журналиста.
    """
    try:
        PAGINATOR_COUNT = 10

        person = Person.objects.get(user=request.user)
        posts = NewsPost.objects.filter(
            author=person
        )

        posts_count = NewsPost.objects.filter(
            author=person.user,
            is_published=True
        ).count()

        context = {
            'person': person,
            'posts_count': posts_count
        }
        return render(request, 'main/journalist/news_create.html', context)

    except Person.DoesNotExist:
        pass
