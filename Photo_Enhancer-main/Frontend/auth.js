// Authentication Module
const API_BASE = 'http://127.0.0.1:8000';

const Auth = {
    isAuthenticated: false,
    user: null,

    // Check if user is authenticated
    async checkAuth() {
        try {
            const response = await fetch(`${API_BASE}/accounts/api/check-auth/`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            this.isAuthenticated = data.authenticated;
            this.user = data.user || null;
            return data.authenticated;
        } catch (error) {
            console.error('Auth check error:', error);
            return false;
        }
    },

    // Login
    async login(username, password) {
        try {
            const response = await fetch(`${API_BASE}/accounts/api/login/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.isAuthenticated = true;
                this.user = data.user;
                return { success: true, data };
            } else {
                const data = await response.json();
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Signup
    async signup(username, email, password, firstName = '') {
        try {
            const response = await fetch(`${API_BASE}/accounts/api/signup/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password, first_name: firstName })
            });

            if (response.ok) {
                const data = await response.json();
                this.isAuthenticated = true;
                this.user = data.user;
                return { success: true, data };
            } else {
                const data = await response.json();
                return { success: false, error: data.error || 'Signup failed' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Logout
    async logout() {
        try {
            await fetch(`${API_BASE}/accounts/api/logout/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            this.isAuthenticated = false;
            this.user = null;
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
};
