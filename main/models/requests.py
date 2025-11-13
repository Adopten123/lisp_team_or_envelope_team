from django.db import models

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
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='student_requests')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='requests')
    type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload_json = models.JSONField(default=dict, blank=True)  # детали: куда выдать, на кого, цель и т.п.

    class Meta:
        verbose_name = "Заявление студента"
        verbose_name_plural = "Заявления студентов"

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
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='teacher_requests')
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='requests')
    type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload_json = models.JSONField(default=dict, blank=True) # детали: куда выдать, на кого, цель и т.п.

    class Meta:
        verbose_name = "Заявление преподавателя"
        verbose_name_plural = "Заявления преподавателей"

    def __str__(self):
        return f"{self.teacher}: {self.get_type_display()} [{self.get_status_display()}]"

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


class AdmissionRequest(models.Model):
    STUDY_FORM_CHOICES = [
        ('full_time', 'Очная'),
        ('part_time', 'Очно-заочная'),
        ('extramural', 'Заочная'),
    ]

    # Поля формы
    last_name = models.CharField("Фамилия", max_length=128)
    first_name = models.CharField("Имя", max_length=128)
    middle_name = models.CharField("Отчество", max_length=128, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=20)
    desired_program = models.CharField("Желаемая программа", max_length=255)
    study_form = models.CharField("Форма обучения", max_length=20, choices=STUDY_FORM_CHOICES, default='full_time')
    previous_education = models.CharField("Предыдущее образование", max_length=255, blank=True)
    comments = models.TextField("Комментарии", blank=True)

    # Системные поля
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