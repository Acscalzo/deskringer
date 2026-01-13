// Authentication helper functions
const Auth = {
    /**
     * Get the stored JWT token
     * @returns {string|null} JWT token or null if not found
     */
    getToken() {
        return localStorage.getItem('admin_token');
    },

    /**
     * Save JWT token to localStorage
     * @param {string} token - JWT token to save
     */
    setToken(token) {
        localStorage.setItem('admin_token', token);
    },

    /**
     * Check if user is authenticated
     * @returns {boolean} True if token exists
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Get headers with authentication
     * @returns {Object} Headers object with Content-Type and Authorization
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    },

    /**
     * Logout user - clear token and redirect to login
     */
    logout() {
        localStorage.removeItem('admin_token');
        window.location.href = '/index.html';
    }
};

/**
 * Require authentication - redirect to login if not authenticated
 * Call this at the start of any page that requires auth
 */
function requireAuth() {
    if (!Auth.isAuthenticated()) {
        window.location.href = '/index.html';
    }
}

/**
 * Logout function for global use
 */
function logout() {
    Auth.logout();
}
