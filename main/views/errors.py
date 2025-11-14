from django.shortcuts import render

def error_400(request, exception):
    context = {
        "title": "Неверный запрос",
        "message": "На сервер был отправлен некорректный запрос.",
        "additional_info": str(exception),
    }
    return render(request, 'main/errors/error.html', context, status=400)

def error_403(request, exception):
    context = {
        "title": "Доступ запрещён",
        "message": "У вас нет прав для просмотра этой страницы.",
        "additional_info": str(exception),
    }
    return render(request, 'main/errors/error.html', context, status=403)

def error_404(request, exception):
    context = {
        "title": "Страница не найдена",
        "message": "Такой страницы не существует.",
        "additional_info": str(exception),
    }
    return render(request, 'main/errors/error.html', context, status=404)

def error_500(request):
    context = {
        "title": "Ошибка сервера",
        "message": "Произошла внутренняя ошибка сервера.",
        "additional_info": "",
    }
    return render(request, 'main/errors/error.html', context, status=500)
