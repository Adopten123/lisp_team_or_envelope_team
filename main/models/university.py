from django.db import models

class University(models.Model):
    """
    Университет
    """
    name = models.CharField("Название университета", max_length=256, unique=True) # название
    short_name = models.CharField("Короткое имя", max_length=64, unique=True) # скоращенное название
    city = models.CharField("Город", max_length=128, blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        verbose_name = "Университет"
        verbose_name_plural = "Университеты"

    def __str__(self):
        return self.short_name or self.name

class Faculty(models.Model):
    """
    Факультет
    убрать null=True из поля university на этапе продакшена
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties', null=True)
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"

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
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"
        unique_together = [("faculty", "name")]

    def __str__(self):
        return f"{self.code or ''} {self.name}".strip()