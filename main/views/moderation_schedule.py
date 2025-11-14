from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from main.forms import ScheduleSlotForm, ScheduleExceptionForm
from main.utils.permissions import is_moderator_min
from main.views.moderation import _resolve_current_university

from main.models import (
    Person, StudentGroup,
)

def moderation_schedule_slot_create(request):
    """
    Страница создания пары
    """
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 1):
        context = {
            "title": "Доступ запрещён",
            "message": "Только Модератор 1 уровня и выше может создавать пары.",
            "additional_info": "Обратитесь к администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    group_id = request.GET.get("group")
    group = get_object_or_404(StudentGroup, pk=group_id) if group_id else None
    uni = _resolve_current_university(user)

    if request.method == "POST":
        form = ScheduleSlotForm(request.POST, university=uni, group=group)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.university = uni
            slot.save()
            form.save_m2m()
            messages.success(request, "Ячейка расписания добавлена.")
            back = f"{reverse('moderation_schedules')}?group={group.id}" if group else reverse('moderation_schedules')
            return redirect(back)
    else:
        form = ScheduleSlotForm(university=uni, group=group)

    context = {
        "current_university": uni,
        "current_group": group,
        "form": form,
    }

    return render(request, 'main/moderation/moderation_schedules_slot_form.html', context)

def moderation_schedule_exception_create(request):
    """
    Страница создания переноса пары
    """
    user = Person.objects.filter(pk=5).first().user

    if not is_moderator_min(user, 1):
        context = {
            "title": "Доступ запрещён",
            "message": "Только Модератор 1 уровня и выше может создавать перенос пары.",
            "additional_info": "Обратитесь к администратору.",
        }
        return render(request, 'main/errors/error.html', context, status=403)

    uni = _resolve_current_university(user)

    if request.method == "POST":
        form = ScheduleExceptionForm(request.POST, university=uni)
        if form.is_valid():
            form.save()
            messages.success(request, "Исключение добавлено.")
            redirect_group = request.GET.get("group") or ""
            return redirect(f"{reverse('moderation_schedules')}?group={redirect_group}")
    else:
        form = ScheduleExceptionForm(university=uni)

    context = {
        "current_university": uni,
        "form": form,
    }
    return render(request, 'main/moderation/moderation_schedules_exception_form.html', context)