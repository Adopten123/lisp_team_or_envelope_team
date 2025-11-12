import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.contrib.auth import login
from main.models import Person

@csrf_exempt
@require_http_methods(["POST"])
def max_auth_view(request):
    """
    API endpoint для автоматической авторизации через WebApp
    """
    try:
        # Парсим JSON данные
        data = json.loads(request.body)
        user_data = data.get('user', {})
        
        if not user_data:
            return JsonResponse({
                'success': False,
                'error': 'User data not provided'
            }, status=400)
        
        # Извлекаем данные пользователя
        vk_user_id = user_data.get('id')
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        username = user_data.get('username', '')
        
        if not vk_user_id:
            return JsonResponse({
                'success': False,
                'error': 'User ID not provided'
            }, status=400)
        
        # Ищем пользователя по vk_user_id
        try:
            person = Person.objects.get(vk_user_id=vk_user_id)
            
        except Person.DoesNotExist:
            # Создаем нового пользователя
            person = Person.objects.create(
                vk_user_id=vk_user_id,
                first_name=first_name,
                last_name=last_name,
                email="",  # временный email
                is_active=True
            )
        
        # Логиним пользователя
        login(request, person)
        
        # Обновляем данные пользователя, если они изменились
        if person.first_name != first_name or person.last_name != last_name:
            person.first_name = first_name
            person.last_name = last_name
            person.save()
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': person.id,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'email': person.email,
                'vk_user_id': person.vk_user_id
            },
            'message': 'Authorization successful'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)

def get_csrf_token(request):
    """
    Endpoint для получения CSRF токена
    """
    return JsonResponse({'csrfToken': get_token(request)})

@require_http_methods(["GET"])
def get_current_user(request):
    """
    Endpoint для получения данных текущего пользователя
    """
    if request.user.is_authenticated and isinstance(request.user, Person):
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'vk_user_id': request.user.vk_user_id
            }
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'user': None
        })

@require_http_methods(["POST"])
def logout_view(request):
    """
    Endpoint для выхода из системы
    """
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logout completed'})

