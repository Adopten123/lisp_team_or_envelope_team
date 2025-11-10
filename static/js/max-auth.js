// max-auth.js
class MaxAppAuth {
    constructor() {
        this.isMaxApp = false;
        this.webAppData = null;
        this.userData = null;
        this.init();
    }

    init() {
        // Проверяем, загружена ли библиотека MAX
        if (typeof window.MAX === 'undefined') {
            console.log('MAX Web App library not loaded');
            this.showGuestMode();
            return;
        }

        this.isMaxApp = true;
        this.initMaxApp();
    }

    async initMaxApp() {
        try {
            // Инициализируем MAX Web App
            await window.MAX.init();
            
            // Получаем данные веб-приложения
            this.webAppData = window.MAX.initData;
            
            console.log('MAX Web App initialized:', this.webAppData);
            
            // Если есть пользователь, обновляем интерфейс и отправляем данные на сервер
            if (this.webAppData && this.webAppData.user) {
                this.userData = this.webAppData.user;
                this.updateUserInterface();
                await this.sendDataToServer();
            } else {
                this.showGuestMode();
            }
            
        } catch (error) {
            console.error('Error initializing MAX Web App:', error);
            this.showGuestMode();
        }
    }

    updateUserInterface() {
        const userCard = document.getElementById('userCard');
        const userName = userCard.querySelector('.user-name');
        const userStatus = userCard.querySelector('.user-status');
        const userBadge = document.getElementById('userBadge');

        if (this.userData) {
            // Форматируем имя пользователя
            const fullName = [this.userData.first_name, this.userData.last_name]
                .filter(Boolean)
                .join(' ') || 'Пользователь MAX';
            
            userName.textContent = fullName;
            userStatus.textContent = this.userData.username ? `@${this.userData.username}` : 'Студент';
            userBadge.classList.add('connected');
            userBadge.textContent = '✓';
            
            // Добавляем аватар, если есть фото
            if (this.userData.photo_url) {
                const avatar = userCard.querySelector('.avatar-placeholder');
                avatar.textContent = '';
                avatar.style.backgroundImage = `url(${this.userData.photo_url})`;
                avatar.style.backgroundSize = 'cover';
                avatar.style.backgroundPosition = 'center';
            }
        }
    }

    showGuestMode() {
        const userBadge = document.getElementById('userBadge');
        userBadge.style.background = '#ffa502';
        userBadge.textContent = '!';
    }

    async sendDataToServer() {
        try {
            const response = await fetch('/api/max-auth/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    init_data: this.webAppData,
                    user_id: this.userData.id,
                    auth_date: this.webAppData.auth_date,
                    hash: this.webAppData.hash
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('User authenticated successfully');
                this.showAuthSuccess();
            } else {
                console.error('Authentication failed:', data.error);
                this.showAuthError();
            }

        } catch (error) {
            console.error('Error sending data to server:', error);
            this.showAuthError();
        }
    }

    showAuthSuccess() {
        // Можно добавить визуальное подтверждение авторизации
        const userCard = document.getElementById('userCard');
        userCard.classList.add('success');
        
        // Показываем временное сообщение
        this.showToast('Авторизация успешна!', 'success');
    }

    showAuthError() {
        this.showToast('Ошибка авторизации', 'error');
    }

    showToast(message, type = 'info') {
        // Создаем элемент тоста
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#2ed573' : type === 'error' ? '#ff4757' : '#3742fa'};
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            z-index: 1000;
            font-size: 0.9rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        
        document.body.appendChild(toast);
        
        // Удаляем тост через 3 секунды
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 3000);
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}