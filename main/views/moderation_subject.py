# main/views/subject_admin.py
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect, render

from main.models import (
    Person, University, Discipline, Curriculum, Teaching, Enrollment
)
from main.forms import (
    DisciplineCreateForm, CurriculumCreateForm, TeachingCreateForm
)
from main.utils.permissions import is_moderator_min
from django.core.paginator import Paginator
from main.views.moderation import _resolve_current_university


# =====DISCIPLINES=====

def moderation_disciplines_list(request):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    qs = Discipline.objects.all().order_by("title")

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(code__icontains=q))

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    context = {
        "current_university": uni,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
    }
    return render(request, "main/moderation/moderation_subjects_disciplines_list.html", context)


def moderation_discipline_edit(request, pk: int):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    discipline = get_object_or_404(Discipline, pk=pk)

    if request.method == "POST":
        form = DisciplineCreateForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            messages.success(request, "Дисциплина обновлена.")
            return redirect("disciplines_list")
        else:
            messages.error(request, "Проверьте форму.")
    else:
        form = DisciplineCreateForm(instance=discipline)

    context = {
        "current_university": uni,
        "form": form,
        "item": discipline,
    }
    return render(request, "main/moderation/moderation_subjects_discipline_edit.html", context)


def moderation_discipline_delete(request, pk: int):
    user = Person.objects.filter(pk=5).first().user

    if request.method != "POST":
        raise Http404()
    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    discipline = get_object_or_404(Discipline, pk=pk)

    with transaction.atomic():
        curricula = Curriculum.objects.filter(discipline=discipline)
        teachings = Teaching.objects.filter(curriculum__in=curricula)
        Enrollment.objects.filter(teaching__in=teachings).delete()
        teachings.delete()
        curricula.delete()
        discipline.delete()

    messages.success(request, "Дисциплина и все связанные сущности удалены.")
    return redirect("disciplines_list")


# =====CURRICULUM=====

def moderation_curriculum_list(request):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    qs = (Curriculum.objects
          .filter(program__faculty__university=uni)
          .select_related("program", "discipline", "program__faculty")
          .order_by("program__name", "discipline__title"))

    # Поиск по программе/дисциплине/коду
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(program__name__icontains=q) |
            Q(discipline__title__icontains=q) |
            Q(discipline__code__icontains=q)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    context = {
        "current_university": uni,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
    }

    return render(request, "main/moderation/moderation_subjects_curriculum_list.html", context)


def moderation_curriculum_edit(request, pk: int):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    item = get_object_or_404(Curriculum, pk=pk, program__faculty__university=uni)

    if request.method == "POST":
        form = CurriculumCreateForm(request.POST, instance=item, university=uni)
        if form.is_valid():
            form.save()
            messages.success(request, "Учебный план обновлён.")
            return redirect("curriculum_list")
        else:
            messages.error(request, "Проверьте форму.")
    else:
        form = CurriculumCreateForm(instance=item, university=uni)

    context = {
        "current_university": uni,
        "form": form,
        "item": item,
    }

    return render(request, "main/moderation/subjects_curriculum_edit.html", context)


def moderation_curriculum_delete(request, pk: int):
    user = Person.objects.filter(pk=5).first().user

    if request.method != "POST":
        raise Http404()
    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    item = get_object_or_404(Curriculum, pk=pk, program__faculty__university=uni)

    with transaction.atomic():
        teachings = Teaching.objects.filter(curriculum=item)
        Enrollment.objects.filter(teaching__in=teachings).delete()
        teachings.delete()
        item.delete()

    messages.success(request, "Учебный план и связанные курсы/зачисления удалены.")
    return redirect("curriculum_list")


# =====TEACHING=====

def moderation_teaching_list(request):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    qs = (Teaching.objects
          .filter(teacher__university=uni)
          .select_related("teacher__person", "curriculum__discipline", "curriculum__program", "group")
          .order_by("-academic_year", "curriculum__discipline__title"))

    # Поиск по ФИО, дисциплине, группе, году
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(teacher__person__last_name__icontains=q) |
            Q(teacher__person__first_name__icontains=q) |
            Q(curriculum__discipline__title__icontains=q) |
            Q(group__name__icontains=q) |
            Q(academic_year__icontains=q)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    context =  {
        "current_university": uni,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
    }

    return render(request, "main/moderation/subjects_teaching_list.html", context)


def moderation_teaching_edit(request, pk: int):
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    item = get_object_or_404(
        Teaching.objects.select_related("teacher__person", "curriculum__discipline", "group"),
        pk=pk, teacher__university=uni
    )

    if request.method == "POST":
        form = TeachingCreateForm(request.POST, instance=item, university=uni)
        if form.is_valid():
            form.save()
            messages.success(request, "Курс (teaching) обновлён.")
            return redirect("teaching_list")
        else:
            messages.error(request, "Проверьте форму.")
    else:
        form = TeachingCreateForm(instance=item, university=uni)

    context = {
        "current_university": uni,
        "form": form,
        "item": item,
    }

    return render(request, "main/moderation/subjects_teaching_edit.html", context)


def moderation_teaching_delete(request, pk: int):
    user = Person.objects.filter(pk=5).first().user

    if request.method != "POST":
        raise Http404()
    if not is_moderator_min(user, 2):
        return HttpResponseForbidden("Недостаточно прав")

    uni = _resolve_current_university(user)
    item = get_object_or_404(Teaching, pk=pk, teacher__university=uni)

    with transaction.atomic():
        Enrollment.objects.filter(teaching=item).delete()
        item.delete()

    messages.success(request, "Курс и все его зачисления удалены.")
    return redirect("teaching_list")
