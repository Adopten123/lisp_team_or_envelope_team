from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from ..models import NewsPost, Person

def news_view(request):
    """
    Функция для просмотра новостей.
    Новости видят все роли.
    Студент видит новости университета и новости группы.

    Изменить: захардкоденного студента
    """
    PAGINATOR_COUNT = 10

    qs = NewsPost.objects.filter(is_published=True).order_by("-published_at")
    person = Person.objects.filter(pk=1).first()

    if person:
        student = getattr(person, "student", None)
        if student:
            uni = student.university
            qs = qs.filter(university=uni)
        else:
            teacher = getattr(person, "teacher", None)
            if teacher:
                qs = qs.filter(university=teacher.university)
    paginator = Paginator(qs, PAGINATOR_COUNT)
    page = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'main/news/news_list.html', {
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    })

def news_detail_view(request, news_id):
    post = get_object_or_404(NewsPost, pk=news_id, is_published=True)
    return render(request, "main/news/news_detail.html",
                  {"post": post}
    )