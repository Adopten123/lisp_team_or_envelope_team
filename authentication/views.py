import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.contrib.auth import login, authenticate
from main.models import Person
from django.contrib.auth.models import User
from datetime import datetime

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
        email = user_data.get('email', '')

        
        if not vk_user_id:
            return JsonResponse({
                'success': False,
                'error': 'User ID not provided'
            }, status=400)
        
        # Ищем пользователя по vk_user_id
        try:
            person = Person.objects.get(vk_user_id=vk_user_id)
            user = person.user
            
        except Person.DoesNotExist:
            user, user_created = User.objects.get_or_create( 
                username=f"max_{vk_user_id}",
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'password': 'none_password',
                    'last_login': datetime.now()
                }
            )
            
            # Создаем нового Person
            person, person_created = Person.objects.get_or_create( 
                vk_user_id=vk_user_id,
                defaults={
                    'user': user,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )

        # Логиним пользователя
        login(request, user)

        # Обновляем данные пользователя, если они изменились
        if person.first_name != person.user.first_name or person.last_name != person.user.last_name:
            person.first_name = person.user.first_name
            person.last_name = person.user.last_name
            person.save()

        return JsonResponse({
            'success': True,
            'user': {
                'id': person.id,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'email': person.email,
                'vk_user_id': person.vk_user_id,
                'last_login': str(person.user.last_login)
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

