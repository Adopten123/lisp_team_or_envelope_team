from django.conf import settings
from django.db import models


class Applicant(models.Model):
    """
    Абитуриент

    В основном вопрос в том, где хранить дату рождения и прочие данные, пока пускай будет тут.
    """
    person = models.OneToOneField('Person', on_delete=models.CASCADE, related_name='applicant')
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=255, blank=True)
    school_name = models.CharField(max_length=255, blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)

    linked_student = models.OneToOneField(
        'Student', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Связь после зачисления"
    )

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"

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
        verbose_name = "Результат экзамена абитуриента"
        verbose_name_plural = "Результаты экзаменов абитуриента"
        unique_together = [("applicant", "subject", "exam_type")]


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
        choices=[
            ('new', 'Новое'),
            ('review', 'На рассмотрении'),
            ('accepted', 'Принято'),
            ('rejected', 'Отклонено')
        ],
        default='new'
    )

    class Meta:
        verbose_name = "Заявление на поступление"
        verbose_name_plural = "Заявления на поступление"

    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.desired_program}"