// API Configuration
const API_BASE_URL = 'https://deskringer-api.onrender.com';

// API Endpoints
const API = {
    LOGIN: `${API_BASE_URL}/api/portal/login`,
    ME: `${API_BASE_URL}/api/portal/me`,
    STATS: `${API_BASE_URL}/api/portal/stats`,
    CALLS: `${API_BASE_URL}/api/portal/calls`,
    CALL: (id) => `${API_BASE_URL}/api/portal/calls/${id}`,
    MARK_HANDLED: (id) => `${API_BASE_URL}/api/portal/calls/${id}/mark-handled`,
    MARK_UNHANDLED: (id) => `${API_BASE_URL}/api/portal/calls/${id}/mark-unhandled`,
    SETTINGS: `${API_BASE_URL}/api/portal/settings`,
    CHANGE_PASSWORD: `${API_BASE_URL}/api/portal/change-password`,
};

// Auth helpers
const Auth = {
    getToken: () => localStorage.getItem('customerToken'),
    setToken: (token) => localStorage.setItem('customerToken', token),
    removeToken: () => localStorage.removeItem('customerToken'),
    isAuthenticated: () => !!Auth.getToken(),

    getHeaders: () => {
        const headers = {
            'Content-Type': 'application/json'
        };
        const token = Auth.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }
};

// Redirect if not authenticated (use on protected pages)
function requireAuth() {
    if (!Auth.isAuthenticated()) {
        window.location.href = '/index.html';
    }
}

// Logout function
function logout() {
    Auth.removeToken();
    window.location.href = '/index.html';
}
