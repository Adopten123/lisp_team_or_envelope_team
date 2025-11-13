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
            const params = new URLSearchParams(window.WebApp.initData);
            const data = {};
        
            for (const [key, value] of params.entries()) {
                if (key === 'user' || key === 'chat') {
                    try {
                        data[key] = JSON.parse(decodeURIComponent(value));
                    } catch (e) {
                        data[key] = value;
                    }
                } else {
                    data[key] = value;
                }
            }
            
            console.log('Платформа: ', window.WebApp.platform);
            console.log('WebApp пользователь:', data.user.id);
            
            // Автоматическая авторизация на бэкенде
            await this.authenticateWithBackend(data);
            
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
                    user: userData.user,
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
