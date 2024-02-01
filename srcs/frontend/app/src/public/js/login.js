import { router, api_url } from './main.js';

export function getLoginPage() {
    fetch('public/html/login-form.html')
        .then(response => response.text())
        .then(template => {
            document.getElementById('main').innerHTML = template;
            document.getElementById('registerLink').addEventListener('click', function(event) {
                event.preventDefault();
                router('register');
            });
            document.querySelector('.card-body').addEventListener('submit', function(event) {
                event.preventDefault();
                var usr_email = document.getElementById('emailField').value;
                var usr_password = document.getElementById('passwordField').value;
                if (!usr_email || !usr_password) {
                    var errorMessage = document.getElementById('error-message');
                    errorMessage.textContent = 'Please fill out all fields';
                    return;
                }
                fetch(api_url + 'auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: usr_email,
                        password: usr_password,
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.refresh) {
                        localStorage.setItem('refreshToken', data.refresh);
                        localStorage.setItem('accessToken', data.access);
                        var errorMessage = document.getElementById('error-message');
                        errorMessage.textContent = '';
                        router('home');
                    } else {
                        var errorMessage = document.getElementById('error-message');
                        errorMessage.textContent = 'Invalid email or password';
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            });
        });
}
