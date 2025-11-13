from django.shortcuts import render

def render_under_development(request, title="Страница в разработке",
                           message="Скоро здесь появится новый функционал.",
                           additional_info=None):
    """
    Универсальная функция для отображения страниц в разработке
    """
    context = {
        'title': title,
        'message': message,
        'additional_info': additional_info,
    }
    return render(request, "main/teacher/working_off_placeholder.html", context)