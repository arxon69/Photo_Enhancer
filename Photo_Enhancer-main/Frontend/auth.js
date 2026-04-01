// Authentication Module
// Dynamically set API_BASE from current origin
const API_BASE = window.location.origin || 'http://127.0.0.1:8000';

const Auth = {
    isAuthenticated: false,
    user: null,

    // Get CSRF token from cookie
    getCookie(name) {
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
    },

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

    // Login - supports both email and username
    async login(emailOrUsername, password) {
        try {
            const response = await fetch(`${API_BASE}/accounts/api/login/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ username: emailOrUsername, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.isAuthenticated = true;
                this.user = data.user;
                return { success: true, data };
            } else {
                const data = await response.json();
                return { success: false, error: data.error || 'Invalid credentials' };
            }
        } catch (error) {
            console.error('Login error:', error);
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
                    'X-CSRFToken': this.getCookie('csrftoken'),
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
            console.error('Signup error:', error);
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
                    'X-CSRFToken': this.getCookie('csrftoken'),
                }
            });

            this.isAuthenticated = false;
            this.user = null;
            return { success: true };
        } catch (error) {
            console.error('Logout error:', error);
            return { success: false, error: error.message };
        }
    }
};
