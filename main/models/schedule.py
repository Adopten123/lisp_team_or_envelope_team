from django.db import models
from django.core.exceptions import ValidationError

class ScheduleSlot(models.Model):
    """
    Класс пары, т.е. повторяющаяся ячейка расписания
    Привязана к университету и teaching
    Может быть для одно одной или несколько групп (поток)
    Поддержка верхней/нижней недели и диапазона дат
    """
    WEEKDAY = [
        (1, "Понедельник"),
        (2, "Вторник"),
        (3, "Среда"),
        (4, "Четверг"),
        (5, "Пятница"),
        (6, "Суббота"),
        (7, "Воскресенье"),
    ]
    PARITY = [
        ("all", "Каждую"),
        ("odd", "Нечётные"),
        ("even", "Чётные"),
    ]

    university = models.ForeignKey(
        'University', on_delete=models.CASCADE, related_name="schedule_slots", verbose_name="Университет"
    )
    teaching = models.ForeignKey(
        'Teaching', on_delete=models.CASCADE, related_name="schedule_slots", verbose_name="Курс (Teaching)"
    )
    groups = models.ManyToManyField(
        'StudentGroup', related_name="schedule_slots", blank=True, verbose_name="Группы"
    )

    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY, verbose_name="День недели")
    start_time = models.TimeField(verbose_name="Начало")
    end_time = models.TimeField(verbose_name="Конец")
    week_parity = models.CharField(
        max_length=5, choices=PARITY, default="all", verbose_name="Чётность недели"
    )

    start_date = models.DateField(verbose_name="Дата начала периода")
    end_date = models.DateField(verbose_name="Дата окончания периода")

    building = models.CharField(max_length=64, blank=True, verbose_name="Корпус")
    room = models.CharField(max_length=32, blank=True, verbose_name="Аудитория")
    note = models.CharField(max_length=128, blank=True, verbose_name="Примечание")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пара"
        verbose_name_plural = "Пары"
        ordering = ["weekday", "start_time"]
        indexes = [
            models.Index(fields=["university", "weekday", "start_time"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        subj = self.teaching.curriculum.discipline.title
        grp = ", ".join(self.groups.values_list("name", flat=True)) or (
            self.teaching.group.name if self.teaching.group else "Поток")
        return f"{subj} — {grp} — {self.get_weekday_display()} {self.start_time}-{self.end_time}"

    # --- Валидация бизнес-логики ---
    def clean(self):
        errs = {}
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            errs["end_time"] = "Время окончания должно быть позже времени начала."
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errs["end_date"] = "Дата окончания должна быть не раньше даты начала."
        if self.university_id and self.teaching_id:
            if self.teaching.teacher.university_id != self.university_id:
                errs["teaching"] = "Teaching должен относиться к этому же университету."
        if errs:
            raise ValidationError(errs)

    # --- Утилиты для выборок ---
    def applies_on_date(self, date_obj, term_start=None):
        """
        Проверяет, попадает ли дата под слот и по чётности.
        term_start - дата начала отсчёта чётности (если None — берём start_date).
        """
        if not (self.start_date <= date_obj <= self.end_date):
            return False
        if self.weekday != date_obj.isoweekday():
            return False
        if self.week_parity == "all":
            return True
        # чётность недели: считаем недели от term_start (или start_date)
        base = term_start or self.start_date
        delta_weeks = (date_obj - base).days // 7
        is_even = (delta_weeks % 2 == 0)
        return (self.week_parity == "even" and is_even) or (self.week_parity == "odd" and not is_even)

    def effective_for_date(self, date_obj):
        """
        Возвращает кортеж (is_cancelled, start_time, end_time, building, room, note, effective_date)
        с учётом исключений на указанную дату (cancel/move/change_room).
        Если слот не применяется к дате - вернёт None.
        """
        if not self.applies_on_date(date_obj):
            return None

        ex = self.exceptions.filter(date=date_obj).order_by("-id").first()
        if not ex:
            return (False, self.start_time, self.end_time, self.building, self.room, self.note, date_obj)

        if ex.action == "cancel":
            return (True, None, None, None, None, None, date_obj)

        # move/change_room
        start = ex.new_start_time or self.start_time
        end = ex.new_end_time or self.end_time
        bld = ex.new_building or self.building
        room = ex.new_room or self.room
        note = ex.new_note or self.note
        eff_date = ex.new_date or date_obj
        return (False, start, end, bld, room, note, eff_date)

class ScheduleException(models.Model):
    """
    Исключение в расписании:
    1) cancel - отмена пары
    2) move - перенос (можно поменять дату/время/аудиторию/примечание)
    3) change_room - смена аудитории/примечания
    """
    ACTIONS = [
        ("cancel", "Отмена"),
        ("move", "Перенос"),
        ("change_room", "Смена аудитории/примечания"),
    ]

    slot = models.ForeignKey(
        'ScheduleSlot', on_delete=models.CASCADE, related_name="exceptions", verbose_name="Ячейка"
    )
    date = models.DateField(verbose_name="Дата")
    action = models.CharField(max_length=12, choices=ACTIONS, verbose_name="Действие")

    # для move / change_room:
    new_date = models.DateField(null=True, blank=True, verbose_name="Новая дата")
    new_start_time = models.TimeField(null=True, blank=True, verbose_name="Новое начало")
    new_end_time = models.TimeField(null=True, blank=True, verbose_name="Новый конец")
    new_building = models.CharField(max_length=64, blank=True, verbose_name="Новый корпус")
    new_room = models.CharField(max_length=32, blank=True, verbose_name="Новая аудитория")
    new_note = models.CharField(max_length=128, blank=True, verbose_name="Новое примечание")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Пара (перенос)"
        verbose_name_plural = "Пары (перенос)"
        ordering = ["date", "slot_id"]
        indexes = [
            models.Index(fields=["date", "action"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} — {self.date} — {self.slot}"

    def clean(self):
        errs = {}

        if self.action == "move":
            if not self.new_start_time or not self.new_end_time:
                errs["new_start_time"] = "Для переноса укажите новое время начала и конца."
            elif self.new_start_time >= self.new_end_time:
                errs["new_end_time"] = "Новое время окончания должно быть позже начала."

        if self.action == "change_room":
            if not (self.new_room or self.new_building or self.new_note):
                errs["new_room"] = "Для смены аудитории/примечания заполните хотя бы одно поле."

        if errs:
            raise ValidationError(errs)