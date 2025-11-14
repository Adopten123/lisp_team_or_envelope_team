from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Prefetch
from django.urls import reverse

from main.utils.permissions import is_moderator_min
from main.utils.week import monday_of

from main.forms import (
    TeacherCreateForm, ProgramCreateForm, FacultyCreateForm,
    DisciplineCreateForm, CurriculumCreateForm, TeachingCreateForm,
    ModerationActionForm, FilterForm, STUDENT_ACTIONS, TEACHER_ACTIONS
)

from main.models import (
    Person, Teacher, University,
    Role, Faculty, Program,
    Enrollment, Student,
    StudentGroup, ScheduleSlot, ScheduleException,
    StudentRequest, TeacherRequest,
)


def _resolve_current_university(user):
    """
    Функция для получения уровня модератора.
    Функция рекомендуема для внутреннего использования внутри файлов: moderation(...).py
    На данный момент функция временная, так как Role будет убрана на этапе продакшена.
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
    """
    Страница модерирования персонала университета.
    На данной странцие можно просмотреть актуальный состав преподавателей,
    добавить новых сотрудников или удалить уволенных сотрудников.
    """
    PAGINATOR_COUNT = 20

    user = Person.objects.filter(pk=5).first().user
    # Только модераторы 2 и 3 уровня
    if not is_moderator_min(user, 2):
        context = {
            "title": "Доступ запрещён",
            "message": "Только Модератор 2 уровня и выше может редактировать персонал.",
            "additional_info": "Обратитесь к администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    current_university = _resolve_current_university(user)

    if not current_university:
        messages.error(request, "В системе нет ни одного университета.")
        context = {
            "current_university": None,
            "page_obj": None,
            "paginator": None,
            "can_manage": False,
            "form": None,
            "department_q": "",
        }
        return render(request, 'main/moderation/moderation_staff.html', context)

    department_q = (request.GET.get("department") or "").strip()

    teachers_qs = (
        Teacher.objects
        .filter(university=current_university)
        .select_related("person", "university")
        .order_by("person__last_name", "person__first_name")
    )
    if department_q:
        teachers_qs = teachers_qs.filter(department__icontains=department_q)

    paginator = Paginator(teachers_qs, PAGINATOR_COUNT)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            form = TeacherCreateForm(request.POST)
            if form.is_valid():
                form.save(university=current_university)
                messages.success(request, "Преподаватель создан, роль человека переключена на Teacher.")
                return redirect('moderation_staff')
            else:
                messages.error(request, "Проверьте форму — есть ошибки.")
        elif action == "delete":
            # удаление Teacher -> Person.role = Guest
            teacher_id = request.POST.get("teacher_id")
            try:
                t = Teacher.objects.select_related("person").get(id=teacher_id, university=current_university)
            except Teacher.DoesNotExist:
                messages.error(request, "Преподаватель не найден в текущем университете.")
            else:
                guest_role, _ = Role.objects.get_or_create(permission="Guest", defaults={"name": "Гость"})
                p = t.person
                t.delete()
                p.role = guest_role
                p.save(update_fields=["role"])
                messages.success(request, "Учётка преподавателя удалена, роль человека переключена на Guest.")
            return redirect('moderation_staff')
        else:
            messages.error(request, "Неизвестное действие.")
            return redirect('moderation_staff')
    else:
        form = TeacherCreateForm()

    context = {
        "current_university": current_university,
        "page_obj": page_obj,
        "paginator": paginator,
        "can_manage": True,
        "form": form,
        "department_q": department_q,
    }

    return render(request, 'main/moderation/moderation_staff.html', context)

def moderation_university(request):
    """
    Страница взаимодействия с факультетами и кафедрами
    """
    user = Person.objects.filter(pk=5).first().user
    err_context = {
        "title": "Доступ запрещён",
        "message": "Только Модератор 2 уровня и выше может создавать факультеты.",
        "additional_info": "Обратитесь к администратору.",
    }
    if not is_moderator_min(user, 2):
        return render(request, 'main/errors/error.html', err_context, status=403)

    current_university = _resolve_current_university(user)

    if not current_university:
        messages.error(request, "Нет университета для управления.")
        context = {
            "current_university": None,
            "faculties": [],
            "can_create_faculty": False,
            "program_form": None,
            "faculty_form": None,
        }
        return render(request, 'main/moderation/moderation_university.html', context)

    can_create_faculty = is_moderator_min(user, 3)

    faculty_form = FacultyCreateForm()
    program_form = ProgramCreateForm(university=current_university)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_faculty":
            if not can_create_faculty:
                return render(request, 'main/errors/error.html', err_context, status=403)

            faculty_form = FacultyCreateForm(request.POST)
            if faculty_form.is_valid():
                faculty_form.save(university=current_university)
                messages.success(request, "Факультет создан.")
                return redirect('moderation_university')
            else:
                messages.error(request, "Проверьте данные факультета.")
        elif action == "create_program":
            program_form = ProgramCreateForm(request.POST, university=current_university)
            if program_form.is_valid():
                program_form.save()
                messages.success(request, "Кафедра/направление создано.")
                return redirect('moderation_university')
            else:
                messages.error(request, "Проверьте данные кафедры/направления.")

    faculties = (Faculty.objects
        .filter(university=current_university)
        .prefetch_related(Prefetch("programs", queryset=Program.objects.order_by("name")))
        .order_by("name")
    )

    context = {
        "current_university": current_university,
        "faculties": faculties,
        "can_create_faculty": can_create_faculty,
        "faculty_form": faculty_form,
        "program_form": program_form,
    }

    return render(request, 'main/moderation/moderation_university.html', context)

def moderation_schedules(request):
    """
    Страница взаимодействия с расписанием
    """

    user = Person.objects.filter(pk=5).first().user
    person = Person.objects.filter(pk=5).first()
    current_university = _resolve_current_university(user)

    if not is_moderator_min(user, 1):
        context = {
            "title": "Доступ запрещён",
            "message": "Только Модератор 1 уровня и выше может редактировать расписание.",
            "additional_info": "Обратитесь к администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    q = (request.GET.get("q") or "").strip()
    groups = (StudentGroup.objects
              .filter(university=current_university)
              .select_related("program", "university")
              .order_by("name")
    )

    if q:
        groups = groups.filter(Q(name__icontains=q) | Q(program__name__icontains=q))

    group_id = request.GET.get("group")
    group = get_object_or_404(StudentGroup, pk=group_id) if group_id else None

    today = timezone.localdate()
    week = {i: [] for i in range(1, 7 + 1)}

    if group:
        slots = (
            ScheduleSlot.objects
            .filter(university_id=group.university_id)
            .filter(Q(groups__id=group.id) | Q(teaching__group_id=group.id))
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

        for slot in slots:
            week[slot.weekday].append({
                "slot": slot,
                "today_effective": slot.effective_for_date(today),
            })

    context = {
        "perm": "Moderator_3lvl",
        "q": q,
        "groups": groups,
        "group": group,
        "week": week,
        "today": today,
        "weekdays": range(1, 8),
    }
    return render(request, 'main/moderation/moderation_schedules_home.html', context)


def moderation_subjects(request):
    """
    Страница редактирования дисциплин, учебных планов и курсов
    """
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        context = {
            "title": "Доступ запрещён",
            "message": "Только Модератор 2 уровня и выше может редактировать дисциплины.",
            "additional_info": "Обратитесь к администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    current_university = _resolve_current_university(user)

    if not current_university:
        messages.error(request, "Нет университета для управления.")
        context = {
            "current_university": None,
            "discipline_form": None,
            "curriculum_form": None,
            "teaching_form": None,
        }
        return render(request, 'main/moderation/moderation_subjects.html', context)

    discipline_form = DisciplineCreateForm()
    curriculum_form = CurriculumCreateForm(university=current_university)
    teaching_form = TeachingCreateForm(university=current_university)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_discipline":
            discipline_form = DisciplineCreateForm(request.POST)
            if discipline_form.is_valid():
                discipline_form.save()
                messages.success(request, "Дисциплина создана.")
                return redirect('moderation_subjects')
            else:
                messages.error(request, "Проверьте данные дисциплины.")

        elif action == "create_curriculum":
            curriculum_form = CurriculumCreateForm(request.POST, university=current_university)
            if curriculum_form.is_valid():
                curriculum_form.save()
                messages.success(request, "Строка учебного плана создана.")
                return redirect('moderation_subjects')
            else:
                messages.error(request, "Проверьте данные учебного плана.")

        elif action == "create_teaching":
            teaching_form = TeachingCreateForm(request.POST, university=current_university)
            if teaching_form.is_valid():
                with transaction.atomic():
                    teaching = teaching_form.save()
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
                return redirect('moderation_subjects')
            else:
                messages.error(request, "Проверьте данные проведения курса.")

        else:
            messages.error(request, "Неизвестное действие.")

    context = {
        "current_university": current_university,
        "discipline_form": discipline_form,
        "curriculum_form": curriculum_form,
        "teaching_form": teaching_form,
    }
    return render(request, 'main/moderation/moderation_subjects.html', context)

def moderation_requests(request):
    """
    Страница обработки справок
    """
    STUDENT_ALLOWED = {"in_progress", "approved", "rejected", "issued"}
    TEACHER_ALLOWED = {"in_review", "approved", "rejected", "issued"}
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        context = {
            "title": "Доступ запрещён",
            "message": "Только Модератор 2 уровня и выше может обрабатывать заявки.",
            "additional_info": "Обратитесь к администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    current_university = _resolve_current_university(user)

    if request.method == "POST" and "obj_id" in request.POST:
        form = ModerationActionForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest("Неверные данные")
        model = form.cleaned_data["model"]
        obj_id = form.cleaned_data["obj_id"]
        new_status = form.cleaned_data["new_status"]

        if model == "student":
            if new_status not in STUDENT_ALLOWED:
                return HttpResponseBadRequest("Недопустимый статус")
            obj = StudentRequest.objects.filter(id=obj_id, university=current_university).first()
            if not obj:
                return HttpResponseBadRequest("Заявка не найдена")
            obj.status = new_status
            obj.save(update_fields=["status", "updated_at"])
        elif model == "teacher":
            if new_status not in TEACHER_ALLOWED:
                return HttpResponseBadRequest("Недопустимый статус")
            obj = TeacherRequest.objects.filter(id=obj_id, university=current_university).first()
            if not obj:
                return HttpResponseBadRequest("Заявка не найдена")
            obj.status = new_status
            obj.save(update_fields=["status", "updated_at"])
        return redirect(reverse('moderation_requests'))

    f = FilterForm(request.GET or None)

    s_qs = StudentRequest.objects.filter(university=current_university)
    t_qs = TeacherRequest.objects.filter(university=current_university)

    source = f.data.get("source") or ""
    req_type = f.data.get("req_type") or ""
    status = f.data.get("status") or ""
    q = (f.data.get("q") or "").strip()
    date_from = f.data.get("date_from") or ""
    date_to = f.data.get("date_to") or ""

    show_student = source in ("", "student")
    show_teacher = source in ("", "teacher")

    def apply_common_filters(qs, type_field="type", status_field="status", json_note_field="payload_json__note"):
        if req_type:
            qs = qs.filter(**{type_field: req_type})
        if status:
            qs = qs.filter(**{status_field: status})
        if q:
            qs = qs.filter(
                Q(**{f"{type_field}__icontains": q}) |
                Q(**{f"{status_field}__icontains": q}) |
                Q(**{f"{json_note_field}__icontains": q})
            )
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs

    if show_student:
        s_qs = apply_common_filters(s_qs)
    else:
        s_qs = s_qs.none()

    if show_teacher:
        t_qs = apply_common_filters(t_qs)
    else:
        t_qs = t_qs.none()

    items = []
    for r in s_qs.select_related("student__person").order_by("-created_at"):
        items.append({
            "model": "student",
            "id": r.id,
            "created_at": r.created_at,
            "type": r.get_type_display(),
            "type_value": r.type,
            "status": r.status,
            "status_display": r.get_status_display(),
            "who": str(r.student.person),
            "note": (r.payload_json or {}).get("note"),
        })
    for r in t_qs.select_related("teacher__person").order_by("-created_at"):
        items.append({
            "model": "teacher",
            "id": r.id,
            "created_at": r.created_at,
            "type": r.get_type_display(),
            "type_value": r.type,
            "status": r.status,
            "status_display": r.get_status_display(),
            "who": str(r.teacher.person),
            "note": (r.payload_json or {}).get("note"),
        })

    items.sort(key=lambda x: x["created_at"], reverse=True)

    paginator = Paginator(items, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    type_choices_union = [
        *StudentRequest.TYPE_CHOICES,
        *TeacherRequest.TYPE_CHOICES,
    ]

    seen = set()
    type_choices = []
    for v, l in type_choices_union:
        if v not in seen:
            seen.add(v)
            type_choices.append((v, l))

    status_choices_union = [
        *StudentRequest.STATUS_CHOICES,
        *TeacherRequest.STATUS,
    ]
    seen = set()
    status_choices = []
    for v, l in status_choices_union:
        if v not in seen:
            seen.add(v)
            status_choices.append((v, l))

    context = {
        "current_university": current_university,
        "page_obj": page_obj,
        "type_choices": type_choices,
        "status_choices": status_choices,
        "source": source,
        "req_type": req_type,
        "status": status,
        "q": q,
        "date_from": date_from,
        "date_to": date_to,
        "STUDENT_ACTIONS": dict(STUDENT_ACTIONS),
        "TEACHER_ACTIONS": dict(TEACHER_ACTIONS),
    }
    return render(request, 'main/moderation/moderation_request_page.html', context)

def moderation_acts(request):
    """
    Страница модерирования актов
    """
    return render_under_development(
        request,
        title="🛠️ Функционал модерирования актов",
        message="Скоро здесь появится полный функционал модерирования актов.",
        additional_info="Вы сможете модерировать акты."
    )