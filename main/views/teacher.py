from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from django.utils import timezone

from main.models import (
    Person, Teaching, ScheduleSlot,
    TeacherRequest,
)
from main.forms import (
    TeacherRequestCreateForm, TeacherNotificationForm
)

def teacher_schedule_view(request):

    person = Person.objects.filter(pk=2).first()
    teacher = getattr(person, "teacher", None) if person else None

    if not teacher:
        return HttpResponseForbidden("Доступно только для преподавателя")

    today = timezone.localdate()

    slots = (
        ScheduleSlot.objects
        .filter(university_id=teacher.university_id)
        .filter(teaching__teacher_id=teacher.id)
        .select_related(
            "teaching",
            "teaching__curriculum",
            "teaching__curriculum__discipline",
            "teaching__teacher",
            "teaching__teacher__person",
        )
        .prefetch_related("groups", "exceptions")
        .distinct()
        .order_by("weekday", "start_time")
    )

    week = {i: [] for i in range(1, 8)}  # 1..7
    for slot in slots:
        week[slot.weekday].append({
            "slot": slot,
            "today_effective": slot.effective_for_date(today),
        })

    context = {
        "teacher": teacher,
        "week": week,
        "today": today,
    }

    return render(request, "main/schedule/teacher_schedule.html", context)

def teacher_subjects_view(request):

    PAGINATOR_COUNT = 10

    person = Person.objects.filter(pk=2).first()
    teacher = getattr(person, "teacher", None) if person else None

    if not teacher:
        return HttpResponseForbidden("Доступно только для преподавателя")

    year = request.GET.get("year")
    sem = request.GET.get("sem")

    qs = (
        Teaching.objects
        .filter(teacher=teacher)
        .select_related("curriculum__discipline", "group")
        .annotate(
            students_total=Count("enrollments", distinct=True),
            assessments_total=Count("assessments", distinct=True),
        )
        .order_by("-academic_year", "-semester_in_year", "curriculum__discipline__title")
    )
    if year:
        qs = qs.filter(academic_year=year)
    if sem in {"1", "2"}:
        qs = qs.filter(semester_in_year=int(sem))

    paginator = Paginator(qs, PAGINATOR_COUNT)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    items = []
    for t in page_obj.object_list:
        items.append({
            "discipline": t.curriculum.discipline.title,
            "group": t.group.name,
            "academic_year": t.academic_year,
            "semester": "осенний" if t.semester_in_year == 1 else "весенний",
            "students_total": t.students_total,
            "assessments_total": t.assessments_total,
        })

    context = {
        "items": items,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "filter_year": year or "",
        "filter_sem": sem or "",
    }

    return render(request, 'main/teacher/teacher_subjects.html', context)

def teacher_working_off_view(request):
    return render(request, "main/teacher/working_off_placeholder.html")

def teacher_request_form(request):
    user = Person.objects.filter(pk=2).first().user
    person = getattr(user, "person", None)
    teacher = getattr(person, "teacher", None) if person else None
    if not teacher:
        return HttpResponseForbidden("Доступно только преподавателям")

    current_university = teacher.university

    # создание
    if request.method == "POST":
        form = TeacherRequestCreateForm(request.POST)
        if form.is_valid():
            obj: TeacherRequest = form.save(commit=False)
            obj.university = current_university
            obj.teacher = teacher
            # оборачиваем текст «примечание» в payload_json
            note = (request.POST.get("note") or "").strip()
            obj.payload_json = {"note": note} if note else {}
            obj.save()
            return redirect(reverse("teacher_request_form"))
    else:
        form = TeacherRequestCreateForm()

    # фильтры
    f_type = request.GET.get("type") or ""
    f_status = request.GET.get("status") or ""
    q = (request.GET.get("q") or "").strip()

    qs = (TeacherRequest.objects
          .filter(university=current_university, teacher=teacher)
          .order_by("-created_at"))

    if f_type:
        qs = qs.filter(type=f_type)
    if f_status:
        qs = qs.filter(status=f_status)
    if q:
        qs = qs.filter(
            Q(type__icontains=q) |
            Q(status__icontains=q) |
            Q(payload_json__note__icontains=q)
        )

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "current_university": current_university,
        "form": form,
        "type_choices": TeacherRequest.TYPE_CHOICES,
        "status_choices": TeacherRequest.STATUS,
        "f_type": f_type, "f_status": f_status, "q": q,
        "page_obj": page_obj,
    }
    return render(request, "main/requests/teacher_request_page.html", context)

def teacher_make_alert_form(request):
    user = Person.objects.filter(pk=2).first().user
    person = getattr(user, "person", None)
    if not person or not hasattr(person, "teacher"):
        return HttpResponseForbidden("Доступно только преподавателям.")

    teacher = person.teacher
    university = teacher.university

    if request.method == "POST":
        form = TeacherNotificationForm(request.POST, teacher=teacher, university=university)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.university = university
            obj.sender = person
            obj.save()
            messages.success(request, "Оповещение отправлено выбранной группе.")
            return redirect("teacher_make_alert")
    else:
        form = TeacherNotificationForm(teacher=teacher, university=university)

    return render(request, "main/notifications/teacher_form.html", {
        "current_university": university,
        "form": form,
    })