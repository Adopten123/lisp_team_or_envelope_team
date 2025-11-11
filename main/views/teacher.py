from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from main.models import Person, Teaching


def teacher_schedule_view(request):
    return HttpResponse("Страница расписания преподавателя")

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
    return HttpResponse("Страница отработок преподавателя")

def teacher_request_form(request):
    return HttpResponse("Страница написания заявлений")

def teacher_make_alert_form(request):
    return HttpResponse("Страница создания оповещения о паре учителем")