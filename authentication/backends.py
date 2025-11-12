# backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from main.models import Person

class VKAuthBackend(ModelBackend):
    """
    Бэкенд аутентификации через VK User ID
    """
    def authenticate(self, request, vk_user_id=None, **kwargs):
        if vk_user_id:
            try:
                # Ищем Person по vk_user_id и получаем связанного User
                person = Person.objects.select_related('user').get(vk_user_id=vk_user_id)
                if person.user and self.user_can_authenticate(person.user):
                    return person.user
            except Person.DoesNotExist:
                return None
        return None