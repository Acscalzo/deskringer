// API Helper Functions

async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: Auth.getHeaders()
        });

        // Check for 401 Unauthorized - JWT expired or invalid
        if (response.status === 401) {
            console.warn('JWT expired or invalid. Logging out...');
            Auth.logout();
            window.location.href = '/index.html';
            throw new Error('Session expired. Please log in again.');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.msg || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Customer API
const CustomerAPI = {
    login: async (email, password) => {
        return await apiRequest(API.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    getMe: async () => {
        return await apiRequest(API.ME);
    },

    getStats: async () => {
        return await apiRequest(API.STATS);
    },

    changePassword: async (currentPassword, newPassword) => {
        return await apiRequest(API.CHANGE_PASSWORD, {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
    },

    updateSettings: async (settings) => {
        return await apiRequest(API.SETTINGS, {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
    }
};

// Call API
const CallAPI = {
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams(params);
        return await apiRequest(`${API.CALLS}?${queryParams}`);
    },

    getById: async (id) => {
        return await apiRequest(API.CALL(id));
    },

    markHandled: async (id) => {
        return await apiRequest(API.MARK_HANDLED(id), {
            method: 'POST'
        });
    },

    markUnhandled: async (id) => {
        return await apiRequest(API.MARK_UNHANDLED(id), {
            method: 'POST'
        });
    }
};
