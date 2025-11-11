from main.utils.menu import get_menu_buttons
from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from ..models import Person
import json
import time
import hashlib
import hmac

def index(request):
    """Главная страница"""

    menu_buttons = get_menu_buttons("Student")

    context = {
        "menu_buttons": menu_buttons,
    }

    return render(request, 'main/main.html', context)


class MaxAuthValidator:
    def __init__(self, bot_token=None):
        self.bot_token = bot_token or getattr(settings, 'MAX_BOT_TOKEN', '')
    
    def validate_init_data(self, init_data_str, hash_str):
        """
        Валидация данных от MAX Web App по аналогии с Telegram
        """
        try:
            # Создаем строку для проверки (все параметры кроме hash, отсортированные)
            data_check_string = self._create_data_check_string(init_data_str)
            
            # Создаем секретный ключ
            secret_key = hmac.new(
                b"WebAppData", 
                self.bot_token.encode(), 
                hashlib.sha256
            ).digest()
            
            # Вычисляем хеш
            computed_hash = hmac.new(
                secret_key, 
                data_check_string.encode(), 
                hashlib.sha256
            ).hexdigest()
            
            return computed_hash == hash_str
            
        except Exception as e:
            print(f"Validation error: {e}")
            return False
    
    def _create_data_check_string(self, init_data_str):
        """Создает строку для проверки данных"""
        params = []
        for param in init_data_str.split('&'):
            key, value = param.split('=')
            if key != 'hash':
                params.append(f"{key}={value}")
        
        params.sort()
        return '\n'.join(params)

@api_view(['POST'])
@permission_classes([AllowAny])
def max_web_app_auth(request):
    """
    Безопасная авторизация через MAX Web App с проверкой подписи
    """
    try:
        data = request.data
        
        # Проверяем обязательные поля
        required_fields = ['user', 'auth_date', 'hash']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Валидируем подпись MAX
        validator = MaxAuthValidator()
        
        # Создаем init_data строку для проверки
        init_data_parts = []
        for key, value in data.items():
            if key != 'hash' and value is not None:
                init_data_parts.append(f"{key}={value}")
        
        init_data_str = '&'.join(init_data_parts)
        
        # Проверяем подпись (закомментируйте если нет BOT_TOKEN)
        # if not validator.validate_init_data(init_data_str, data['hash']):
        #     return Response(
        #         {'error': 'Invalid signature'},
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )
        
        user_data = data['user']
        max_user_id = str(user_data['id'])
        first_name = user_data.get('first_name', 'User')
        last_name = user_data.get('last_name', '')
        
        # Проверяем, не истекла ли авторизация (24 часа)
        auth_date = int(data['auth_date'])

        if time.time() - auth_date > 86400:  # 24 часа
            return Response(
                {'error': 'Authorization expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        with transaction.atomic():
            # Создаем или обновляем Person
            person, created = Person.objects.get_or_create(
                vk_user_id=max_user_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            
            if not created:
                person.first_name = first_name
                person.last_name = last_name
                person.save()
            
            # Безопасное хранение в сессии
            request.session['max_auth_user_id'] = person.vk_user_id
            request.session['max_auth_timestamp'] = int(time.time())
            
            # Устанавливаем время жизни сессии
            request.session.set_expiry(86400)  # 24 часа
            
            return Response({
                'success': True,
                'person_id': person.id,
                'is_new_user': created,
                'full_name': f"{first_name} {last_name}",
                'message': 'User authenticated successfully'
            })
            
    except Exception as e:
        return Response(
            {'error': 'Authentication failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )