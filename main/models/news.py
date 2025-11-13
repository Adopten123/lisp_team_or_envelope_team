from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError

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
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news_detail", kwargs={"news_id": self.id})

class GroupNotification(models.Model):
    """
    Групповое оповещение (видно только студентам указанной группы).
    Отправитель — преподаватель или студент-староста.
    """
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name="group_notifications")
    group = models.ForeignKey('StudentGroup', on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey('Person', on_delete=models.PROTECT, related_name="sent_notifications")

    icon = models.CharField("Иконка/эмодзи", max_length=8, default="🔔", blank=True)
    text = models.TextField("Текст", max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Групповое оповещение"
        verbose_name_plural = "Групповые оповещения"
        indexes = [
            models.Index(fields=["group", "created_at"]),
        ]

    def __str__(self):
        who = f"{self.sender.last_name} {self.sender.first_name}"
        return f"[{self.group}] {self.icon} {self.text[:40]} — {who}"

    def clean(self):
        # базовая консистентность университета
        if self.group and self.university_id and self.group.university_id != self.university_id:
            raise ValidationError({"group": "Группа должна относиться к тому же университету."})
