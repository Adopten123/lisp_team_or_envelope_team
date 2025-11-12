from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q, Prefetch

from main.utils.permissions import is_moderator_min
from main.forms import TeacherCreateForm, ProgramCreateForm, FacultyCreateForm
from main.models import Person, Teacher, University, Role, Faculty, Program


def _resolve_current_university(user):
    """
    Простейшая стратегия, чтобы взять «текущий университет» модератора:
    - если у Person есть teacher -> его university
    - иначе если есть student -> его university
    - иначе первый в базе (fallback)
    При желании замени на свой механизм (например, хранить в сессии).
    """
    person = getattr(user, "person", None)
    if person:
        teacher = getattr(person, "teacher", None)
        if teacher and teacher.university_id:
            return teacher.university
        student = getattr(person, "student", None)
        if student and student.university_id:
            return student.university
    return University.objects.order_by("id").first()

def moderation_staff(request):

    user = Person.objects.filter(pk=5).first().user
    # Только модераторы 2 и 3 уровня
    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    current_uni = _resolve_current_university(user)
    if not current_uni:
        messages.error(request, "В системе нет ни одного университета.")
        return render(request, "main/moderation/moderation_staff.html", {
            "current_university": None,
            "page_obj": None,
            "paginator": None,
            "can_manage": False,
            "form": None,
            "department_q": "",
        })

    # Фильтр по кафедре (поиск по contains)
    department_q = (request.GET.get("department") or "").strip()

    teachers_qs = (
        Teacher.objects
        .filter(university=current_uni)
        .select_related("person", "university")
        .order_by("person__last_name", "person__first_name")
    )
    if department_q:
        teachers_qs = teachers_qs.filter(department__icontains=department_q)

    # Пагинация по 20
    paginator = Paginator(teachers_qs, 20)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    # POST-действия
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            form = TeacherCreateForm(request.POST)
            if form.is_valid():
                form.save(university=current_uni)
                messages.success(request, "Преподаватель создан, роль человека переключена на Teacher.")
                return redirect("moderation_staff")
            else:
                messages.error(request, "Проверьте форму — есть ошибки.")
        elif action == "delete":
            # удаление Teacher -> Person.role = Guest
            teacher_id = request.POST.get("teacher_id")
            try:
                t = Teacher.objects.select_related("person").get(id=teacher_id, university=current_uni)
            except Teacher.DoesNotExist:
                messages.error(request, "Преподаватель не найден в текущем университете.")
            else:
                guest_role, _ = Role.objects.get_or_create(permission="Guest", defaults={"name": "Гость"})
                p = t.person
                t.delete()
                p.role = guest_role
                p.save(update_fields=["role"])
                messages.success(request, "Учётка преподавателя удалена, роль человека переключена на Guest.")
            return redirect("moderation_staff")
        else:
            messages.error(request, "Неизвестное действие.")
            return redirect("moderation_staff")
    else:
        form = TeacherCreateForm()

    context = {
        "current_university": current_uni,
        "page_obj": page_obj,
        "paginator": paginator,
        "can_manage": True,
        "form": form,
        "department_q": department_q,
    }

    return render(request, "main/moderation/moderation_staff.html", context)

def moderation_university(request):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    current_uni = _resolve_current_university(user)
    if not current_uni:
        messages.error(request, "Нет университета для управления.")
        return render(request, "main/moderation/moderation_university.html", {
            "current_university": None,
            "faculties": [],
            "can_create_faculty": False,
            "program_form": None,
            "faculty_form": None,
        })

    can_create_faculty = is_moderator_min(user, 3)

    faculty_form = FacultyCreateForm()
    program_form = ProgramCreateForm(university=current_uni)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_faculty":
            if not can_create_faculty:
                return HttpResponseForbidden("Недостаточно прав для создания факультетов")
            faculty_form = FacultyCreateForm(request.POST)
            if faculty_form.is_valid():
                faculty_form.save(university=current_uni)
                messages.success(request, "Факультет создан.")
                return redirect("moderation_university")
            else:
                messages.error(request, "Проверьте данные факультета.")
        elif action == "create_program":
            program_form = ProgramCreateForm(request.POST, university=current_uni)
            if program_form.is_valid():
                program_form.save()
                messages.success(request, "Кафедра/направление создано.")
                return redirect("moderation_university")
            else:
                messages.error(request, "Проверьте данные кафедры/направления.")

    faculties = (
        Faculty.objects.filter(university=current_uni)
        .prefetch_related(Prefetch("programs", queryset=Program.objects.order_by("name")))
        .order_by("name")
    )

    return render(request, "main/moderation/moderation_university.html", {
        "current_university": current_uni,
        "faculties": faculties,
        "can_create_faculty": can_create_faculty,
        "faculty_form": faculty_form,
        "program_form": program_form,
    })

def moderation_schedules(request):
    return HttpResponse(f"Страница редактирования расписания групп")

def moderation_subjects(request):
    return HttpResponse(f"Страница редактирования дисциплин")

def moderation_requests(request):
    return HttpResponse("Страница обработки справок")

def moderation_acts(request):
    return HttpResponse(f"Страница редактирования актов университета")