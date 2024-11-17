// Utility functions
const showAlert = (message, type = 'info') => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
};

const handleError = async (response) => {
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Something went wrong');
    }
    return response.json();
};

// Authentication functions
const login = async (email, password) => {
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: email,
                password: password,
            }),
        });

        const data = await handleError(response);
        localStorage.setItem('token', data.access_token);
        return data;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
};

const register = async (email, username, password) => {
    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                username,
                password,
            }),
        });

        const data = await handleError(response);
        showAlert('Registration successful! Please log in.', 'success');
        return data;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
};

const changePassword = async (currentPassword, newPassword) => {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/v1/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
            }),
        });

        await handleError(response);
        showAlert('Password changed successfully!', 'success');
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
};

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = loginForm.email.value;
            const password = loginForm.password.value;
            
            try {
                await login(email, password);
                window.location.href = '/dashboard';
            } catch (error) {
                console.error('Login failed:', error);
            }
        });
    }

    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = registerForm.email.value;
            const username = registerForm.username.value;
            const password = registerForm.password.value;
            
            try {
                await register(email, username, password);
                window.location.href = '/login';
            } catch (error) {
                console.error('Registration failed:', error);
            }
        });
    }

    // Change password form
    const changePasswordForm = document.getElementById('change-password-form');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = changePasswordForm.currentPassword.value;
            const newPassword = changePasswordForm.newPassword.value;
            const confirmPassword = changePasswordForm.confirmPassword.value;

            if (newPassword !== confirmPassword) {
                showAlert('New passwords do not match', 'error');
                return;
            }

            try {
                await changePassword(currentPassword, newPassword);
                changePasswordForm.reset();
            } catch (error) {
                console.error('Password change failed:', error);
            }
        });
    }
});
