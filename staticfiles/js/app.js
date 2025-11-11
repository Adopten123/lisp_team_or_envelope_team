// app.js
class CampusApp {
    constructor() {
        this.currentPage = 'main';
        this.maxAuth = null;
        this.init();
    }

    init() {
        this.startMaxAuth();
    }

    startMaxAuth() {
        this.maxAuth = new MaxAppAuth();
    }
}

// Инициализация приложения при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    window.campusApp = new CampusApp();
});
