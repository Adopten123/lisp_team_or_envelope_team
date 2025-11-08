from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# === ОБЪЕКТЫ ЛЮДЕЙ ===

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

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    vk_user_id = models.CharField(
        "VK/Max user id", max_length=64, blank=True, db_index=True
    )

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
    Студентческая группа (ПО-51 и проч)
    """
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
