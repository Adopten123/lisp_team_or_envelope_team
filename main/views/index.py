from main.utils.menu import get_menu_buttons
from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import Person
from django.contrib.auth import login
from django.contrib.auth import get_user_model

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
        person = Person.objects.get(vk_user_id=max_user_id)

        # Если у Person есть связанный User - используем его
        if person.user:
            return person.user

        # Если User не существует - создаем его
        User = get_user_model()
        username = f"max_{max_user_id}"
        
        # Создаем User если не существует
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': person.first_name,
                'last_name': person.last_name,
            }
        )
        
        # Связываем Person с User
        if created:
            person.user = user
            person.save()
        
        login(request, user)

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