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

// Admin API
const AdminAPI = {
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

    getTrialCustomers: async () => {
        return await apiRequest(`${API_BASE_URL}/api/admin/trial-customers`);
    }
};

// Customer API
const CustomerAPI = {
    getAll: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API.CUSTOMERS}?${queryString}` : API.CUSTOMERS;
        return await apiRequest(url);
    },

    getById: async (id) => {
        return await apiRequest(API.CUSTOMER(id));
    },

    create: async (customerData) => {
        return await apiRequest(API.CUSTOMERS, {
            method: 'POST',
            body: JSON.stringify(customerData)
        });
    },

    update: async (id, customerData) => {
        return await apiRequest(API.CUSTOMER(id), {
            method: 'PUT',
            body: JSON.stringify(customerData)
        });
    },

    delete: async (id) => {
        return await apiRequest(API.CUSTOMER(id), {
            method: 'DELETE'
        });
    },

    setPassword: async (id, password) => {
        return await apiRequest(API.SET_CUSTOMER_PASSWORD(id), {
            method: 'POST',
            body: JSON.stringify({ password })
        });
    }
};

// Call API
const CallAPI = {
    getAll: async (params = {}) => {
        // Add admin_view=true for admin dashboard
        params.admin_view = 'true';
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API.CALLS}?${queryString}` : API.CALLS;
        return await apiRequest(url);
    },

    getById: async (id) => {
        // Add admin_view=true for admin dashboard
        return await apiRequest(`${API.CALL(id)}?admin_view=true`);
    },

    getRecent: async (limit = 10) => {
        return await apiRequest(`${API.RECENT_CALLS}?limit=${limit}&admin_view=true`);
    }
};

// Stripe API
const StripeAPI = {
    createPaymentLink: async (customerId) => {
        return await apiRequest(`${API_BASE_URL}/api/stripe/create-payment-link/${customerId}`, {
            method: 'POST'
        });
    },

    createCheckoutSession: async (customerId) => {
        return await apiRequest(`${API_BASE_URL}/api/stripe/create-checkout-session/${customerId}`, {
            method: 'POST'
        });
    },

    getSubscriptionStatus: async (customerId) => {
        return await apiRequest(`${API_BASE_URL}/api/stripe/subscription-status/${customerId}`);
    },

    cancelSubscription: async (customerId) => {
        return await apiRequest(`${API_BASE_URL}/api/stripe/cancel-subscription/${customerId}`, {
            method: 'POST'
        });
    }
};
