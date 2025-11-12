from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Q

from main.models import Person, StudentRole, Student

from main.forms import HeadmanNotificationForm

def headman_group_news_view(request):
    student = Student.objects.filter(pk=2).first()

    user = student.person.user
    person = getattr(user, "person", None)

    group = student.student_group

    is_headman = StudentRole.objects.filter(
        student=student, role="headman",
        start_date__lte=timezone.localdate(),
    ).filter(Q(end_date__isnull=True) | Q(end_date__gte=timezone.localdate())).exists()

    if not is_headman:
        return HttpResponseForbidden("Только староста может отправлять оповещения.")

    if request.method == "POST":
        form = HeadmanNotificationForm(
            request.POST,
            university=student.university,
            group=group,
            sender=person,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Оповещение отправлено группе.")
            return redirect("headman_group_news")
    else:
        form = HeadmanNotificationForm(
            university=student.university,
            group=group,
            sender=person,
        )

    context = {
        "current_university": student.university,
        "group": group,
        "form": form,
    }

    return render(request, "main/notifications/headman_form.html", context)