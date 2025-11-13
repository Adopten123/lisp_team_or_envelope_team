from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Enrollment(models.Model):
    """
    Эта модель создана для того, чтобы показывать факт,
    что студент изучает дисциплину по конкретному плану/семестру/группе/году.
    """
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='enrollments')
    teaching = models.ForeignKey('Teaching', on_delete=models.PROTECT, related_name='enrollments')
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
    teaching = models.ForeignKey('Teaching', on_delete=models.CASCADE, related_name='assessments')
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
    assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='assessment_results')
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