from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, reverse
from django.db.models import Q

from main.models import Person, StudentRole, Student, GroupNotification

from main.forms import HeadmanNotificationForm

def headman_group_news_view(request):
    student = Student.objects.filter(pk=2).first()

    user = student.person.user
    person = getattr(user, "person", None)

    group = student.student_group

    is_headman = (StudentRole.objects
        .filter(
            student=student, role="headman",
            start_date__lte=timezone.localdate(),
        )
        .filter(
                Q(end_date__isnull=True) | Q(end_date__gte=timezone.localdate())
        )
        .exists()
    )

    if not is_headman:
        context = {
            "title": "Доступ запрещён",
            "message": "Только староста может отправлять оповещения.",
            "additional_info": "Обратитесь к старосте группы или администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    base_instance = GroupNotification(
        university=student.university,
        group=student.student_group,
        sender=person,
        created_at=timezone.now(),
    )
    if request.method == "POST":
        form = HeadmanNotificationForm(request.POST, instance=base_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Оповещение отправлено группе.")
            return redirect('index')
    else:
        form = HeadmanNotificationForm(initial={"icon": "📰"})

    context = {
        "current_university": student.university,
        "group": group,
        "form": form,
    }

    return render(request, 'main/notifications/headman_form.html', context)