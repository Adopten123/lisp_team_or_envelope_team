// webapp-auth.js - Авторизация через WebApp
class WebAppAuth {
    constructor() {
        this.init();
    }

    async init() {
        // Проверяем, находимся ли мы в WebApp
        if (typeof window.WebApp === 'undefined') {
            console.log('WebApp не обнаружен');
            return;
        }

        await this.initializeWebApp();
    }

    async initializeWebApp() {
        try {
            console.log('1 - Начинаем инициализацию WebApp');

            console.log('2 - WebApp инициализирован');
            
            // Получаем данные пользователя
            const userData = window.WebApp.initData;
            console.log('WebApp пользователь:', userData);
            
            // Автоматическая авторизация на бэкенде
            await this.authenticateWithBackend(userData);
            
        } catch (error) {
            console.error('Ошибка инициализации WebApp:', error);
        }
    }

    async authenticateWithBackend(userData) {
        try {
            console.log('3 - Отправляем данные на бэкенд');
            
            const response = await fetch('/api/max-auth/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    // Передаем только нужные данные пользователя
                    user_id: userData.id,
                    first_name: userData.first_name,
                    last_name: userData.last_name,
                    username: userData.username,
                    photo_url: userData.photo_url,
                    language_code: userData.language_code,
                })
            });

            const data = await response.json();
            console.log('4 - Ответ от бэкенда:', data);

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
    console.log('DOM загружен, запускаем WebAppAuth');
    new WebAppAuth();
});
