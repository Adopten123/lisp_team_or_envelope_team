from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# === МЕНЕДЖЕРЫ МОДЕЛЕЙ ===

class PersonManager(models.Manager):
    def create_from_vk_data(self, data):
        """
        Создает пользователя из данных MAX
        """
        max_user_id = str(data.get('id'))
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        username = data.get('username', '')
    
        
        return self.create(
            vk_user_id=max_user_id,
            first_name=first_name,
            last_name=last_name,
            email='',
            is_active=True
        )

# === ОБЪЕКТЫ ЛЮДЕЙ ===

# models.py
class Person(models.Model):
    """
    Базовый объект человека.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='person', help_text="Связь с Django User (если есть)"
    )

    last_name = models.CharField("Фамилия", max_length=128)
    first_name = models.CharField("Имя", max_length=128)
    middle_name = models.CharField("Отчество", max_length=128, blank=True)
    role = models.ForeignKey('Role', related_name='role', on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    vk_user_id = models.CharField(
        "VK/Max user id", max_length=64, blank=True, db_index=True
    )
    last_login = models.DateTimeField("Последний вход", null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["vk_user_id"])]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Teacher(models.Model):
    """
    Объект учителя.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='teacher')
    academic_title = models.CharField(max_length=128, blank=True)
    department = models.CharField(max_length=255, blank=True)
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='teachers')

    def __str__(self):
        return str(self.person)


class StudentGroup(models.Model):
    """
    Студенческая группа (ПО-51 и проч)

    Убрать null=True на продакшене
    """
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='groups', null=True)
    program = models.ForeignKey('Program', on_delete=models.PROTECT, related_name='groups') # программа обучения
    name = models.CharField(max_length=64)  # ПО-51
    admission_year = models.PositiveSmallIntegerField()  # год начала учебы
    curator = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='curating_groups'
    )

    class Meta:
        unique_together = [("program", "name")]
        indexes = [models.Index(fields=["admission_year"])]

    def __str__(self):
        return self.name

class Student(models.Model):
    """
    Студент

    Поля под вопросом: current_year, по сути дублирование информации
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='student')

    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='students')
    student_group = models.ForeignKey(StudentGroup, on_delete=models.PROTECT, related_name='students')
    student_id = models.CharField("Номер студенческого билета", max_length=32, unique=True)

    current_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)], help_text="Курс (1..6)"
    )
    admission_year = models.PositiveSmallIntegerField() # год поступления

    def __str__(self):
        return f"{self.person} ({self.student_group})"

# === УНИВЕРСИТЕТСКИЕ СТРУКТУРЫ ===

class University(models.Model):
    """
    Университет
    """
    name = models.CharField("Название университета", max_length=256, unique=True) # название
    short_name = models.CharField("Короткое имя", max_length=64, unique=True) # скоращенное название
    city = models.CharField("Город", max_length=128, blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return self.short_name or self.name

class Faculty(models.Model):
    """
    Факультет
    убрать null=True из поля university на этапе продакшена
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties', null=True)
    name = models.CharField(max_length=256)
    def __str__(self):
        return self.name

class Program(models.Model):
    """
    Программа обучения (Программная Инженерия и прочее)
    """
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name='programs')
    name = models.CharField(max_length=255) # название направления
    code = models.CharField(max_length=32, blank=True) # код направления
    duration_years = models.PositiveSmallIntegerField(default=4) # длительность обучения в годах

    class Meta:
        unique_together = [("faculty", "name")]

    def __str__(self):
        return f"{self.code or ''} {self.name}".strip()

class Discipline(models.Model):
    """
    Дисциплина (математика, ООП и т.п.)

    ects - система единиц, которая используется для измерения учебной нагрузки студента
    """
    code = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=256)
    ects = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = [("code", "title")]

    def __str__(self):
        return self.title

class Curriculum(models.Model):
    """
    Класс учебного плана.
    На какой программе и в каком семестре читается дисциплина,
    рекомендуемые часы/контроль и т.п.
    """
    SEMESTER_CHOICES = [(i, f"{i}") for i in range(1, 13)]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='curriculum') # название учебной программы
    discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT, related_name='curriculum_items') #дисциплна
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES) #семестр, в котором изучается программа
    hours = models.PositiveSmallIntegerField(default=0) # количество часов
    control_form = models.CharField(
        max_length=32,
        choices=[("exam", "Экзамен"), ("test", "Зачет"), ("diff_test", "Дифф. зачет")],
        default="exam"
    ) # форма оценивания

    class Meta:
        unique_together = [("program", "discipline", "semester")]

    def __str__(self):
        return f"{self.discipline} {self.program}"

class Teaching(models.Model):
    """
    Класс конкретного курса

    Кто и когда ведёт дисциплину.
    Модель, созданная для связи преподавателя с конкретной группой/потоком и семестром.

    Поля под вопросом: academic_year, semester_in_year
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teachings')
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='teachings')
    group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='teachings')

    academic_year = models.CharField(max_length=9)  # учбеный год
    semester_in_year = models.PositiveSmallIntegerField(choices=[(1, "осенний"), (2, "весенний")])

    class Meta:
        unique_together = [("teacher", "curriculum", "group", "academic_year")]
        indexes = [models.Index(fields=["academic_year"])]

    def __str__(self):
        return f"{self.teacher} → {self.curriculum.discipline}"

# === Амплуа для моделей людей ===

class Role(models.Model):
    """
    Временное решение для выдачи ролей
    """
    PERMISSION = [
        ("Moderator_3lvl", "Модератор 3ур."),
        ("Moderator_2lvl", "Модератор 2ур."),
        ("Moderator_1lvl",  "Модератор 1ур."),
        ("Teacher", "Учитель"),
        ("Journalist", "Журналист"),
        ("Headman", "Модерация группы"),
        ("Student", "Студент"),
        ("Applicant", "Абитуриент"),
        ("Guest", "Гость"),
    ]

    permission = models.CharField(max_length=64, choices=PERMISSION)
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name} - {self.permission}"


class StudentRole(models.Model):
    """
    Роли студентов: староста, журналист, профорг (с историей периодов).
    """
    ROLE_CHOICES = [
        ("headman", "Староста"),
        ("journalist", "Журналист"),
        ("TUO", "Профорг"),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    start_date = models.DateField() # начало срока полномочий
    end_date = models.DateField(null=True, blank=True) # конец срока поломочий

    class Meta:
        indexes = [models.Index(fields=["role", "start_date"])]

    def __str__(self):
        return f"{self.student} — {self.get_role_display()}"

# === СИСТЕМА ОЦЕНИВАНИЯ ===
"""
Достаточно тяжелая абстракция, как мне кажется, но вот пока от нее будем исходить,
Внимательно прочитайте, что писал про это.  Чуть позже напишу отдельный README.md про систему оценивания.
"""
class Enrollment(models.Model):
    """
    Эта модель создана для того, чтобы показывать факт,
    что студент изучает дисциплину по конкретному плану/семестру/группе/году.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    teaching = models.ForeignKey(Teaching, on_delete=models.PROTECT, related_name='enrollments')
    date_enrolled = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("student", "teaching")]
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        return f"{self.student} ↔ {self.teaching}"


class Assessment(models.Model):
    """
    Класс элемента оценивания в рамках конкретной проходимой дисциплины (ДЗ/тест/экзамен и т.п.).
    """
    TYPE_CHOICES = [
        ("hw", "Домашнее задание"),
        ("quiz", "Тест/Квиз"),
        ("lab", "Лабораторная"),
        ("exam", "Экзамен"),
        ("project", "Проект"),
        ("other", "Другое"),
    ]
    teaching = models.ForeignKey(Teaching, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    max_points = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.0,
        help_text="Вес в итоговой оценке (сумма по курсу может быть 1.0 или 100)"
    )
    due_at = models.DateTimeField(null=True, blank=True)
    is_final = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.teaching})"


class AssessmentResult(models.Model):
    """
    Результат студента по конкретной работе. Поддерживает попытки/пересдачи.
    """
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessment_results')
    attempt = models.PositiveSmallIntegerField(default=1)
    points = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    graded_at = models.DateTimeField(auto_now_add=True)

    # Нормируемые представления (опционально): 5-балльная, ECTS
    grade_5 = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(2), MaxValueValidator(5)]
    )
    grade_ects = models.CharField(
        max_length=2, blank=True,
        choices=[("A","A"),("B","B"),("C","C"),("D","D"),("E","E"),("FX","FX"),("F","F")]
    )

    class Meta:
        unique_together = [("assessment", "student", "attempt")]
        indexes = [models.Index(fields=["student", "graded_at"])]

    def __str__(self):
        return f"{self.student} — {self.assessment} = {self.points}"

# === ЗАЯВЛЕНИЯ ===

class StudentRequest(models.Model):
    """
    Заявления студента (включая справки).
    """
    TYPE_CHOICES = [
        ("certificate_enrollment", "Справка об обучении"),
        ("certificate_income", "Справка о доходах/стипендии"),
        ("dormitory", "Общежитие"),
        ("practice", "Практика/стажировка"),
        ("other", "Прочее"),
    ]
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("submitted", "Отправлено"),
        ("in_progress", "В работе"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
        ("issued", "Выдано"),
    ]
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='student_requests')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='requests')
    type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload_json = models.JSONField(default=dict, blank=True)  # детали: куда выдать, на кого, цель и т.п.

    def __str__(self):
        return f"{self.student}: {self.get_type_display()} [{self.get_status_display()}]"

class TeacherRequest(models.Model):
    """
        Заявления преподавателя (включая справки).
    """
    TYPE_CHOICES = [
        ("annual", "Ежегодный отпуск"),
        ("sick", "Больничный"),
        ("academic", "Академический отпуск"),
        ("business", "Командировка"),
        ("other", "Иное"),
    ]
    STATUS = [
        ("submitted", "Отправлено"),
        ("in_review", "На рассмотрении"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
    ]
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='teacher_requests')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='requests')
    type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload_json = models.JSONField(default=dict, blank=True) # детали: куда выдать, на кого, цель и т.п.

    def __str__(self):
        return f"{self.teacher}: {self.get_type_display()} [{self.get_status_display()}]"


# === АБИТУРИЕНТЫ ===

class Applicant(models.Model):
    """
    Абитуриент

    В основном вопрос в том, где хранить дату рождения и прочие данные, пока пускай будет тут.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='applicant')
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=255, blank=True)
    school_name = models.CharField(max_length=255, blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)

    linked_student = models.OneToOneField(
        Student, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Связь после зачисления"
    )

    def __str__(self):
        return f"Абитуриент: {self.person}"


class ApplicantExam(models.Model):
    """Результаты ЕГЭ/вступительных и пр."""
    EXAM_TYPE = [
        ("USE", "ЕГЭ"),
        ("internal", "Внутренний"),
        ("other", "Другое"),
    ]
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='exams')
    subject = models.CharField(max_length=128)
    exam_type = models.CharField(max_length=16, choices=EXAM_TYPE, default="USE")
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = [("applicant", "subject", "exam_type")]


class AdmissionRequest(models.Model):
    """
    Заявка абитуриента на программу (с приоритетами и статусами).
    """
    STATUS = [
        ("draft", "Черновик"),
        ("submitted", "Подано"),
        ("under_review", "На рассмотрении"),
        ("accepted", "Принято"),
        ("rejected", "Отклонено"),
        ("enrolled", "Зачислен"),
    ]
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='admission_request')
    priority = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS, default="submitted")
    submitted_at = models.DateTimeField(auto_now_add=True)
    payload_json = models.JSONField(default=dict, blank=True)  # загрузка файлов/доков/льгот и пр.

    class Meta:
        unique_together = [("applicant", "program")]
        indexes = [models.Index(fields=["status", "priority"])]

    def __str__(self):
        return f"{self.applicant} → {self.program} ({self.status})"

# === НОВОСТИ ===

class NewsPost(models.Model):
    """
    Модель новостей
    """
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='news', null=True)
    news_icon = models.CharField(max_length=8, verbose_name="Эмодзи")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Текст новости")
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(default=timezone.now)
    author = models.CharField(max_length=100, verbose_name="Автор")
    cover_image = models.ImageField(upload_to="news_covers/", blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news_detail", kwargs={"news_id": self.id})

# === РАСПИСАНИЕ ===

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
        University, on_delete=models.CASCADE, related_name="schedule_slots", verbose_name="Университет"
    )
    teaching = models.ForeignKey(
        Teaching, on_delete=models.CASCADE, related_name="schedule_slots", verbose_name="Курс (Teaching)"
    )
    groups = models.ManyToManyField(
        StudentGroup, related_name="schedule_slots", blank=True, verbose_name="Группы"
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
        ScheduleSlot, on_delete=models.CASCADE, related_name="exceptions", verbose_name="Ячейка"
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


class HelpRequest(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Техническая проблема'),
        ('study', 'Учебные вопросы'),
        ('schedule', 'Проблемы с расписанием'),
        ('profile', 'Проблемы с профилем'),
        ('other', 'Другое'),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='technical'
    )
    email = models.EmailField("Email для обратной связи")
    subject = models.CharField("Тема обращения", max_length=255)
    description = models.TextField("Подробное описание проблемы")
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')],
        default='medium'
    )
    is_urgent = models.BooleanField("Срочная проблема", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('new', 'Новый'), ('in_progress', 'В работе'), ('resolved', 'Решено')],
        default='new'
    )

    def __str__(self):
        return f"{self.subject} ({self.get_category_display()})"

    class Meta:
        verbose_name = "Обращение в поддержку"
        verbose_name_plural = "Обращения в поддержку"


class ApplicationRequest(models.Model):
    STUDY_FORM_CHOICES = [
        ('full_time', 'Очная'),
        ('part_time', 'Очно-заочная'),
        ('extramural', 'Заочная'),
    ]

    last_name = models.CharField("Фамилия", max_length=128)
    first_name = models.CharField("Имя", max_length=128)
    middle_name = models.CharField("Отчество", max_length=128, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=20)
    desired_program = models.CharField("Желаемая программа", max_length=255)
    study_form = models.CharField("Форма обучения", max_length=20, choices=STUDY_FORM_CHOICES, default='full_time')
    previous_education = models.CharField("Предыдущее образование", max_length=255, blank=True)
    comments = models.TextField("Комментарии", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('new', 'Новое'), ('review', 'На рассмотрении'), ('accepted', 'Принято'), ('rejected', 'Отклонено')],
        default='new'
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.desired_program}"

    class Meta:
        verbose_name = "Заявление на поступление"
        verbose_name_plural = "Заявления на поступление"