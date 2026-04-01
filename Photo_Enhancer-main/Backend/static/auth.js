// Authentication Module
const Auth = {
    isAuthenticated: false,
    user: null,

    // Helper to get CSRF token
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
            const response = await fetch('/accounts/api/check-auth/', {
                method: 'GET',
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
            const response = await fetch('/accounts/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (response.ok) {
                this.isAuthenticated = true;
                this.user = data.user;
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Signup
    async signup(username, email, password, firstName = '') {
        try {
            const response = await fetch('/accounts/api/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ username, email, password, first_name: firstName })
            });

            const data = await response.json();
            if (response.ok) {
                this.isAuthenticated = true;
                this.user = data.user;
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'Signup failed' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Logout
    async logout() {
        try {
            const response = await fetch('/accounts/api/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                }
            });

            if (response.ok) {
                this.isAuthenticated = false;
                this.user = null;
                return { success: true };
            } else {
                return { success: false, error: 'Logout failed' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
};