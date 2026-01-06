// Theme Management
const ThemeManager = {
    init() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);

        // Add theme toggle button to header
        this.addToggleButton();
    },

    setTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
        localStorage.setItem('theme', theme);
        this.updateToggleButton();
    },

    toggleTheme() {
        const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },

    addToggleButton() {
        const userMenu = document.querySelector('.user-menu');
        if (!userMenu) return;

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'theme-toggle';
        toggleBtn.id = 'theme-toggle-btn';
        toggleBtn.setAttribute('aria-label', 'Toggle theme');
        toggleBtn.onclick = () => this.toggleTheme();

        // Insert before logout button
        userMenu.insertBefore(toggleBtn, userMenu.querySelector('.btn'));
        this.updateToggleButton();
    },

    updateToggleButton() {
        const btn = document.getElementById('theme-toggle-btn');
        if (!btn) return;

        const isDark = document.body.classList.contains('dark-mode');
        btn.textContent = isDark ? '☀️' : '🌙';
        btn.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
    }
};

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
