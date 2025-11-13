from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden

from main.forms import StudentCreateForm
from main.utils.permissions import is_moderator_min

def create_student_view(request):
    """
    Страница создания студента (доступна модераторам 2 уровня и выше).
    """
    user = request.user
    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав для создания студентов")

    if request.method == "POST":
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Студент создан успешно.")
            return redirect("moderation_staff")  # или другая страница
        else:
            messages.error(request, "Проверьте форму — есть ошибки.")
    else:
        form = StudentCreateForm()

    context = {
        "form": form,
        "title": "Создание студента",
    }

    return render(request, "main/auth/create_student.html", context)
