// app.js
class CampusApp {
    constructor() {
        this.currentPage = 'main';
        this.maxAuth = null;
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.initializeNewsCarousel();
        this.startMaxAuth();
        this.adjustScrollForNavigation();
    }

    startMaxAuth() {
        this.maxAuth = new MaxAppAuth();
    }

    adjustScrollForNavigation() {
        // Автоматическая корректировка скролла для фиксированной навигации
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            // Добавляем отступ снизу для комфортного скролла
            mainContent.style.paddingBottom = '20px';
        }
    }

    initializeEventListeners() {
        // Обработчики для быстрых действий
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.handleActionClick(e.currentTarget.dataset.action);
            });
        });

        // Обработчики для навигации
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleNavigation(e.currentTarget.dataset.page);
            });
        });

        // Обработчик изменения ориентации экрана
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.adjustScrollForNavigation();
            }, 300);
        });

        // Обработчик ресайза окна
        window.addEventListener('resize', () => {
            this.adjustScrollForNavigation();
        });
    }

    handleActionClick(action) {
        console.log('Action clicked:', action);
        
        // Визуальная обратная связь
        const card = document.querySelector(`[data-action="${action}"]`);
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);

        // Обработка различных действий
        switch (action) {
            case 'schedule':
                this.showSchedule();
                break;
            case 'grades':
                this.showGrades();
                break;
            case 'group':
                this.showGroup();
                break;
            case 'certificate':
                this.showCertificate();
                break;
            case 'cafeteria':
                this.showCafeteria();
                break;
            case 'sports':
                this.showSports();
                break;
            case 'events':
                this.showEvents();
                break;
            case 'contacts':
                this.showContacts();
                break;
        }
    }

    handleNavigation(page) {
        if (this.currentPage === page) return;
        
        // Обновляем активную кнопку навигации
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');
        
        this.currentPage = page;
        this.showPage(page);
    }

    showPage(page) {
        // Здесь будет логика переключения страниц
        console.log('Navigating to:', page);
        
        // Временное сообщение о функционале
        this.maxAuth.showToast(`Раздел "${this.getPageTitle(page)}" в разработке`);
    }

    getPageTitle(page) {
        const titles = {
            'main': 'Главная',
            'news': 'Новости',
            'profile': 'Профиль',
            'help': 'Помощь'
        };
        return titles[page] || 'Страница';
    }

    initializeNewsCarousel() {
        let currentNewsIndex = 0;
        const newsItems = document.querySelectorAll('.news-item');
        
        if (newsItems.length > 1) {
            setInterval(() => {
                newsItems[currentNewsIndex].classList.remove('active');
                currentNewsIndex = (currentNewsIndex + 1) % newsItems.length;
                newsItems[currentNewsIndex].classList.add('active');
            }, 5000);
        }
    }

    setupSwipeListeners() {
        let startX = 0;
        const newsCarousel = document.querySelector('.news-carousel');
        
        if (!newsCarousel) return;
        
        newsCarousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });
        
        newsCarousel.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const diff = startX - endX;
            
            if (Math.abs(diff) > 50) { // Минимальная дистанция свайпа
                if (diff > 0) {
                    this.nextNews();
                } else {
                    this.prevNews();
                }
            }
        });
    }

    nextNews() {
        const newsItems = document.querySelectorAll('.news-item');
        const currentActive = document.querySelector('.news-item.active');
        let nextIndex = Array.from(newsItems).indexOf(currentActive) + 1;
        
        if (nextIndex >= newsItems.length) nextIndex = 0;
        
        currentActive.classList.remove('active');
        newsItems[nextIndex].classList.add('active');
    }

    prevNews() {
        const newsItems = document.querySelectorAll('.news-item');
        const currentActive = document.querySelector('.news-item.active');
        let prevIndex = Array.from(newsItems).indexOf(currentActive) - 1;
        
        if (prevIndex < 0) prevIndex = newsItems.length - 1;
        
        currentActive.classList.remove('active');
        newsItems[prevIndex].classList.add('active');
    }

    // Методы для различных функциональностей
    showSchedule() {
        this.maxAuth.showToast('Загрузка расписания...');
    }

    showGrades() {
        this.maxAuth.showToast('Загрузка оценок...');
    }

    showGroup() {
        this.maxAuth.showToast('Загрузка моей группы...');
    }

    showCertificate() {
        this.maxAuth.showToast('Загрузка справок...');
    }

    showCafeteria() {
        this.maxAuth.showToast('Меню столовой...');
    }

    showSports() {
        this.maxAuth.showToast('Спортивные мероприятия...');
    }

    showEvents() {
        this.maxAuth.showToast('Культурные события...');
    }

    showContacts() {
        this.maxAuth.showToast('Контакты университета...');
    }
}

// Инициализация приложения при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    window.campusApp = new CampusApp();
});