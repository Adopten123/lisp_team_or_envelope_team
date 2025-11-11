from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Prefetch
from django.shortcuts import render
from django.core.paginator import Paginator

from ..models import Person, Student, Enrollment, Assessment, AssessmentResult, StudentRole
from main.utils.grades_helper import normalize_total, to_5pt
def student_schedule_view(request):
    return HttpResponse("Страница просмотра расписания студентами")

def student_grades_view(request):
    """
    Функция просмотра оценок студента.
    - активные курсы (Enrollment.is_active=True)
    - по каждому курсу: список элементов оценивания и последняя оценка студента
    - расчет итогового процента по весам
    - пагинация по курсам (6 на страницу)

    Изменить: захардкоденный студент
    """
    PAGINATOR_COUNT = 6

    person = Person.objects.filter(pk=1).first()
    student = getattr(person, 'student', None)

    if not student:
        return HttpResponseForbidden("Доступно только для студентов")

    enrollments = (
        Enrollment.objects
        .filter(student=student, is_active=True)
        .select_related(
            "teaching__teacher__person",
            "teaching__curriculum__discipline",
            "teaching__group",
        )
        .prefetch_related(
            Prefetch(
                "teaching__assessments",
                queryset=Assessment.objects.order_by("is_final", "due_at").prefetch_related(
                    Prefetch(
                        "results",
                        queryset=AssessmentResult.objects
                        .filter(student=student)
                        .order_by("-graded_at", "-attempt"),
                        to_attr="student_results",
                    )
                ),
                to_attr="assessments_with_results",
            )
        )
        .order_by("-teaching__academic_year", "-teaching__semester_in_year")
    )

    courses = []
    for enr in enrollments:
        t = enr.teaching
        discipline = t.curriculum.discipline
        teacher_name = str(t.teacher.person)
        group_name = t.group.name if t.group else "Поток"

        items = []
        total_weighted = 0.0
        weight_sum = 0.0

        for a in getattr(t, "assessments_with_results", []):
            res = a.student_results[0] if getattr(a, "student_results", None) else None
            if res:
                max_pts = float(a.max_points) if a.max_points else 0.0
                pts = float(res.points)
                pct = (pts / max_pts * 100.0) if max_pts > 0 else None
                grade_5 = res.grade_5 if res.grade_5 else None
            else:
                pct = None
                grade_5 = None

            if pct is not None:
                total_weighted += pct * float(a.weight)
            weight_sum += float(a.weight)

            items.append({
                "title": a.title,
                "type": a.get_type_display(),
                "max_points": a.max_points,
                "weight": a.weight,
                "due_at": a.due_at,
                "is_final": a.is_final,
                "last_points": (res.points if res else None),
                "last_percent": (round(pct, 2) if pct is not None else None),
                "grade_5": grade_5,
            })

        final_percent = round(normalize_total(total_weighted, weight_sum), 2) if weight_sum > 0 else 0.0
        final_grade5 = to_5pt(final_percent)

        courses.append({
            "discipline": discipline.title,
            "teacher": teacher_name,
            "group": group_name,
            "academic_year": t.academic_year,
            "semester": t.get_semester_in_year_display(),
            "assessments": items,
            "final_percent": final_percent,
            "final_grade5": final_grade5,
        })

    paginator = Paginator(courses, PAGINATOR_COUNT)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    return render(request, "main/grades/student_grades.html", {
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    })

def student_group_view(request):
    """
    Страница просмотра группы студента.
    """
    PAGINATOR_COUNT = 20
    person = Person.objects.filter(pk=1).first()
    student = getattr(person, "student", None) if person else None
    if not student:
        return HttpResponseForbidden("Доступно только для студентов")

    group = student.student_group
    curator = group.curator.person if group else None

    qs = (
        Student.objects
        .filter(student_group=group)
        .select_related("person")
        .prefetch_related(
            Prefetch("roles", queryset=StudentRole.objects.all(), to_attr="roles_data")
        )
        .order_by("person__last_name", "person__first_name", "person__middle_name")
    )

    paginator = Paginator(qs, PAGINATOR_COUNT)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    classmates = []
    headman = None
    for s in page_obj.object_list:
        if s.person.role.permission == "Headman":
            headman = { "name": str(s.person), "student_id": s.student_id, "is_me": s == student }
            continue

        classmates.append({
            "name": str(s.person),
            "student_id": s.student_id,
            "is_me": s == student,
        })

    context = {
        "group_name": group.name,
        "classmates": classmates,
        "curator": curator,
        "headman": headman,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    }
    return render(request, 'main/group/group_list.html', context)

def student_request_view(request):
    return HttpResponse("Страница просмотра справок")