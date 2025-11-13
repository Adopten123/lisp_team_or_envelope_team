from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError


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

    class Meta:
        verbose_name = "Человек"
        verbose_name_plural = "Люди"
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

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return str(self.person)

class Student(models.Model):
    """
    Студент

    Поля под вопросом: current_year, по сути дублирование информации
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='student')

    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='students')
    student_group = models.ForeignKey('StudentGroup', on_delete=models.PROTECT, related_name='students')
    student_id = models.CharField("Номер студенческого билета", max_length=32, unique=True)

    current_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)], help_text="Курс (1..6)"
    )
    admission_year = models.PositiveSmallIntegerField() # год поступления

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return f"{self.person} ({self.student_group})"

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
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        unique_together = [("program", "name")]
        indexes = [models.Index(fields=["admission_year"])]

    def __str__(self):
        return self.name