from main.utils.menu import get_menu_buttons
from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import Person
from django.contrib.auth import login
from django.contrib.auth import login, get_user_model
from django.contrib.auth import authenticate


def index(request):
    """Главная страница"""

    menu_buttons = get_menu_buttons("University Moderator 3lvl")

    context = {
        "menu_buttons": menu_buttons,
    }

    return render(request, 'main/main.html', context)


@api_view(['POST'])
@permission_classes([AllowAny])
def max_web_app_auth(request):
    """
    Безопасная авторизация через MAX Web App с проверкой подписи
    """
    try:
        data = request.data
        
        user_data = data['user']
        max_user_id = str(user_data['id'])
        first_name = user_data.get('first_name', 'User')
        last_name = user_data.get('last_name', '')

        # Ищем Person по vk_user_id
        # Ищем или создаем Person
        person, person_created = Person.objects.get_or_create(
            vk_user_id=max_user_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        # Если Person уже существовал, обновляем данные при необходимости
        if not person_created:
            update_fields = []
            if person.first_name != first_name:
                person.first_name = first_name
                update_fields.append('first_name')
            if person.last_name != last_name:
                person.last_name = last_name
                update_fields.append('last_name')
            
            if update_fields:
                person.save(update_fields=update_fields)

         # Если у Person есть связанный User - используем его
        if person.user:
            user = person.user
            user_created = False
        else:
            # Если User не существует - создаем его
            User = get_user_model()
            username = f"max_{max_user_id}"
            
            # Создаем User если не существует
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            
            # Связываем Person с User
            if user_created:
                person.user = user
                person.save()

        user = person.user
        
        if user:
            login(request, user)

            return Response({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'person': {
                        'id': person.id,
                        'first_name': person.first_name,
                        'last_name': person.last_name,
                        'vk_user_id': person.vk_user_id,
                    },
                    'is_new_user': user_created,
                    'is_new_person': person_created,
                    'full_name': f"{first_name} {last_name}".strip(),
                    'message': 'User authenticated successfully'
                })
        else:
            return Response(
                {'error': 'User authentication failed'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        return Response(
            {'error': 'Authentication failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )