// API Configuration
const API_BASE_URL = 'https://deskringer-api.onrender.com';

// API Endpoints
const API = {
    LOGIN: `${API_BASE_URL}/api/admin/login`,
    ME: `${API_BASE_URL}/api/admin/me`,
    STATS: `${API_BASE_URL}/api/admin/stats`,
    CUSTOMERS: `${API_BASE_URL}/api/customers`,
    CUSTOMER: (id) => `${API_BASE_URL}/api/customers/${id}`,
    CALLS: `${API_BASE_URL}/api/calls`,
    CALL: (id) => `${API_BASE_URL}/api/calls/${id}`,
    RECENT_CALLS: `${API_BASE_URL}/api/calls/recent`,
};

// Auth helpers
const Auth = {
    getToken: () => localStorage.getItem('adminToken'),
    setToken: (token) => localStorage.setItem('adminToken', token),
    removeToken: () => localStorage.removeItem('adminToken'),
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
