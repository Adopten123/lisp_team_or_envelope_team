from functools import wraps
from django.http import JsonResponse
import time
from ..models import Person

def max_login_required(view_func):
    """
    Безопасный декоратор для проверки авторизации через MAX
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Проверяем наличие необходимых данных в сессии
        person_id = request.session.get('max_auth_person_id')
        auth_timestamp = request.session.get('max_auth_timestamp')
        max_user_id = request.session.get('max_auth_user_id')
        
        if not all([person_id, auth_timestamp, max_user_id]):
            return JsonResponse(
                {'error': 'Authentication required'}, 
                status=401
            )
        
        # Проверяем время жизни авторизации (24 часа)
        if time.time() - auth_timestamp > 86400:
            # Очищаем сессию
            request.session.flush()
            return JsonResponse(
                {'error': 'Session expired'}, 
                status=401
            )
        
        # Проверяем, что пользователь все еще существует
        try:
            person = Person.objects.get(
                id=person_id, 
                vk_user_id=max_user_id
            )
            request.person = person  # Добавляем в request для удобства
        except Person.DoesNotExist:
            request.session.flush()
            return JsonResponse(
                {'error': 'User not found'}, 
                status=401
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper


def get_current_person(request):
    """
    Получить текущего авторизованного пользователя
    Возвращает Person или None
    """
    user_id = getattr(request, 'session', {}).get('max_auth_user_id')
    
    if not user_id:
        return None
    
    try:
        return Person.objects.get(
            vk_user_id=user_id
        )
    except Person.DoesNotExist:
        # Очищаем сессию при несоответствии
        request.session.flush()
        return None