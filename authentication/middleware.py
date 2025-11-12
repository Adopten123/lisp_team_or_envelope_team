class PersonMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Добавляем person в request если пользователь аутентифицирован
        if request.user.is_authenticated and hasattr(request.user, 'person'):
            request.person = request.user.person
        else:
            request.person = None
        
        response = self.get_response(request)
        return response