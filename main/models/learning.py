from django.db import models

class Discipline(models.Model):
    """
    Дисциплина (математика, ООП и т.п.)

    ects - система единиц, которая используется для измерения учебной нагрузки студента
    """
    code = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=256)
    ects = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"
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

    program = models.ForeignKey('Program', on_delete=models.CASCADE, related_name='curriculum') # название учебной программы
    discipline = models.ForeignKey('Discipline', on_delete=models.PROTECT, related_name='curriculum_items') #дисциплна
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES) #семестр, в котором изучается программа
    hours = models.PositiveSmallIntegerField(default=0) # количество часов
    control_form = models.CharField(
        max_length=32,
        choices=[("exam", "Экзамен"), ("test", "Зачет"), ("diff_test", "Дифф. зачет")],
        default="exam"
    ) # форма оценивания

    class Meta:
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"
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
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='teachings')
    curriculum = models.ForeignKey('Curriculum', on_delete=models.CASCADE, related_name='teachings')
    group = models.ForeignKey('StudentGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='teachings')

    academic_year = models.CharField(max_length=9)  # учбеный год
    semester_in_year = models.PositiveSmallIntegerField(choices=[(1, "осенний"), (2, "весенний")])

    class Meta:
        verbose_name = "Учебный курс"
        verbose_name_plural = "Учебные курсы"
        unique_together = [("teacher", "curriculum", "group", "academic_year")]
        indexes = [models.Index(fields=["academic_year"])]

    def __str__(self):
        return f"{self.teacher} → {self.curriculum.discipline}"