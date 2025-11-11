// max-auth.js - Только авторизация в Django
class MaxAppAuth {
    constructor() {
        this.init();
    }

    async init() {
        // Проверяем, находимся ли мы в MAX Web App
        if (typeof Window.WebApp === 'undefined') {
            console.log('MAX Web App не обнаружен');
            return;
        }

        await this.initializeMaxApp();
    }

    async initializeMaxApp() {
        try {
            console.log('1');
            // Инициализируем MAX Web App
            await Window.WebApp.init();
            console.log('2');
            // Получаем данные пользователя
            const userData = Window.WebApp.initData.user;
            console.log('MAX пользователь:', userData);
            
            // Автоматическая авторизация на бэкенде
            await this.authenticateWithBackend(userData);
            
        } catch (error) {
            console.error('Ошибка инициализации MAX:', error);
        }
    }

    async authenticateWithBackend(userData) {
        try {
            const response = await fetch('/api/max-auth/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    user: userData,
                    auth_date: Window.WebApp.initData.auth_date,
                    hash: Window.WebApp.initData.hash
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('Авторизация успешна, пользователь сохранен в БД');
            } else {
                console.error('Ошибка авторизации:', data.error);
            }

        } catch (error) {
            console.error('Ошибка связи с сервером:', error);
        }
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

// Автоматическая инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    new MaxAppAuth();
});