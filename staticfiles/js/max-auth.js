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
            console.log('1 - Проверяем платформу');
            
            console.log('Платформа: ', window.WebApp.platform);

            if (window.WebApp.platform === 'web') {
                console.log('Авторизация невозможна - страница открыта в web версии мессенджера')
                this.showWebBrowserMessage();
                return;
            }

            console.log('2 - Получаем данные из WebApp');
            
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
            
            console.log('WebApp пользователь:', data.user.id);
            
            // Автоматическая авторизация на бэкенде
            await this.authenticateWithBackend(data);
            
        } catch (error) {
            console.error('Ошибка инициализации WebApp:', error);
            this.showWebBrowserMessage();
            return;
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

    showWebBrowserMessage() {
        // Создаем сообщение для пользователя
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: #ff6b6b;
            color: white;
            padding: 20px;
            text-align: center;
            font-family: Arial, sans-serif;
            font-size: 16px;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;
        
        messageDiv.innerHTML = `
            <strong>⚠️ Страница открыта в веб-браузере</strong><br>
            Для работы с этим сервисом используйте приложение для Android/IOS/PC
        `;
        
        document.body.appendChild(messageDiv);

        // Скрываем основной контент
        const container = document.querySelector('.container');
        if (container) {
            container.style.opacity = '0.5';
            container.style.pointerEvents = 'none';
        }

        const navMenu = document.querySelector('.bottom-nav');
        if (navMenu) {
            navMenu.style.opacity = '0.9';
            navMenu.style.pointerEvents = 'none';
        }
    }
}

// Автоматическая инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, запускаем WebAppAuth');
    new WebAppAuth();
});
