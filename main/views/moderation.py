from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Prefetch

from main.utils.permissions import is_moderator_min
from main.utils.week import monday_of

from main.forms import (
    TeacherCreateForm, ProgramCreateForm, FacultyCreateForm,
    DisciplineCreateForm, CurriculumCreateForm, TeachingCreateForm
)

from main.models import (
    Person, Teacher, University,
    Role, Faculty, Program,
    Enrollment, Student,
    StudentGroup, ScheduleSlot, ScheduleException
)


def _resolve_current_university(user):
    """
    Простейшая функция, чтобы получить университет модератора:
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

    context = {
        "current_university": current_uni,
        "faculties": faculties,
        "can_create_faculty": can_create_faculty,
        "faculty_form": faculty_form,
        "program_form": program_form,
    }

    return render(request, "main/moderation/moderation_university.html", context)

def moderation_schedules(request):
    import datetime as dt
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 1):
        return HttpResponseForbidden("Недостаточно прав")

    current_university = _resolve_current_university(user)

    group_id = request.GET.get("group")
    group = get_object_or_404(StudentGroup, pk=group_id, university=current_university) if group_id else None

    # неделя
    week_param = request.GET.get("week")
    try:
        base_date = dt.datetime.strptime(week_param, "%Y-%m-%d").date() if week_param else timezone.localdate()
    except Exception:
        base_date = timezone.localdate()
    week_start = monday_of(base_date)
    week_days = [week_start + dt.timedelta(days=i) for i in range(7)]

    # пустая неделя по умолчанию (важно: dict, не None)
    week = {d: [] for d in week_days}

    if group:
        # выбираем слоты для группы: либо M2M groups, либо teaching.group
        slots = (
            ScheduleSlot.objects
            .filter(university=current_university)
            .filter(Q(groups=group) | Q(teaching__group=group))
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

        # заполняем неделю: слот входит в день, если applies_on_date вернул True
        for slot in slots:
            for day in week_days:
                eff = slot.effective_for_date(day)  # учитывает диапазон дат, чётность, исключения
                if not eff:
                    continue
                is_cancelled, start, end, bld, room, note, eff_date = eff
                week[day].append({
                    "slot": slot,
                    "cancelled": bool(is_cancelled),
                    "start": start,
                    "end": end,
                    "building": bld,
                    "room": room,
                    "note": note,
                    "date": eff_date,
                })

        # можно отсортировать пары внутри дня по времени
        for d in week_days:
            week[d].sort(key=lambda x: (x["cancelled"], x["start"] or dt.time(0, 0)))

    context = {
        "current_university": current_university,
        "groups": StudentGroup.objects.filter(university=current_university).order_by("name"),
        "current_group": group,
        "week_start": week_start,
        "week_days": week_days,
        "week": week,  # точно dict
    }
    return render(request, "main/moderation/moderation_schedules_home.html", context)
def moderation_subjects(request):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    current_uni = _resolve_current_university(user)
    if not current_uni:
        messages.error(request, "Нет университета для управления.")
        return render(request, "main/moderation/moderation_subjects.html", {
            "current_university": None,
            "discipline_form": None,
            "curriculum_form": None,
            "teaching_form": None,
        })

    discipline_form = DisciplineCreateForm()
    curriculum_form = CurriculumCreateForm(university=current_uni)
    teaching_form = TeachingCreateForm(university=current_uni)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_discipline":
            discipline_form = DisciplineCreateForm(request.POST)
            if discipline_form.is_valid():
                discipline_form.save()
                messages.success(request, "Дисциплина создана.")
                return redirect("moderation_subjects")
            else:
                messages.error(request, "Проверьте данные дисциплины.")

        elif action == "create_curriculum":
            curriculum_form = CurriculumCreateForm(request.POST, university=current_uni)
            if curriculum_form.is_valid():
                curriculum_form.save()
                messages.success(request, "Строка учебного плана создана.")
                return redirect("moderation_subjects")
            else:
                messages.error(request, "Проверьте данные учебного плана.")

        elif action == "create_teaching":
            teaching_form = TeachingCreateForm(request.POST, university=current_uni)
            if teaching_form.is_valid():
                with transaction.atomic():
                    teaching = teaching_form.save()
                    # Если указана группа — создаём Enrollment всем студентам этой группы
                    group = teaching.group
                    if group:
                        students = Student.objects.filter(student_group=group)
                        created_count = 0
                        for st in students:
                            _, created = Enrollment.objects.get_or_create(
                                student=st, teaching=teaching
                            )
                            if created:
                                created_count += 1
                        messages.success(
                            request,
                            f"Teaching создан. Создано зачислений: {created_count}."
                        )
                    else:
                        messages.success(request, "Teaching создан (без группы/потока).")
                return redirect("moderation_subjects")
            else:
                messages.error(request, "Проверьте данные проведения курса.")

        else:
            messages.error(request, "Неизвестное действие.")

    context = {
        "current_university": current_uni,
        "discipline_form": discipline_form,
        "curriculum_form": curriculum_form,
        "teaching_form": teaching_form,
    }
    return render(request, "main/moderation/moderation_subjects.html", context)

def moderation_requests(request):
    return HttpResponse("Страница обработки справок")

def moderation_acts(request):
    return HttpResponse(f"Страница редактирования актов университета")