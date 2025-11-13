from django.conf import settings
from django.db import models

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
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    start_date = models.DateField() # начало срока полномочий
    end_date = models.DateField(null=True, blank=True) # конец срока поломочий

    class Meta:
        indexes = [models.Index(fields=["role", "start_date"])]

    def __str__(self):
        return f"{self.student} — {self.get_role_display()}"
