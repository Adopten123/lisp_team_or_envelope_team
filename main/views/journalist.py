from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import NewsPost, Person, StudentRole, University


def journalist_news_view(request):
    """
    Функция для добавления новостей.
    Добавление новостей доступно для журналиста.
    """
    try:
        person = Person.objects.filter(pk=5).first()

        if request.method == 'POST':
            # Получаем данные из формы
            news_icon = request.POST.get('news_icon', '').strip()
            title = request.POST.get('title', '').strip()
            body = request.POST.get('body', '').strip()
            cover_image = request.FILES.get('cover_image')

            # Валидация данных
            if not title or not body or not news_icon:
                messages.error(request, 'Все обязательные поля должны быть заполнены.')
                return redirect('journalist_news_view')

            # Получаем университет журналиста (предполагаем, что у журналиста есть университет)
            university = getattr(person, 'university', None) or University.objects.first()

            # Создаем новость
            news_post = NewsPost(
                university=university,
                news_icon=news_icon,
                title=title,
                body=body,
                author=f"{person.last_name} {person.first_name}",
                published_at=timezone.now(),
                is_published=True
            )

            if cover_image:
                news_post.cover_image = cover_image

            news_post.save()

            messages.success(request, 'Новость успешно опубликована!')
            return redirect('journalist_news_view')

        # GET запрос - отображаем форму
        posts_count = NewsPost.objects.filter(
            author=person.__str__(),
            is_published=True
        ).count()

        context = {
            'person': person,
            'posts_count': posts_count
        }
        return render(request, 'main/journalist/news_create.html', context)

    except Person.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('index')
    except Exception as e:
        messages.error(request, f'Произошла ошибка: {str(e)}')
