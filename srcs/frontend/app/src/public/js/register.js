import { router, api_url } from './main.js';

function emailMatch() {
    let email = document.getElementById('email').value;
    let emailConfirm = document.getElementById('verifyEmail').value;
    let errorMessage = document.getElementById('verify-email-error-message');
    if (email === emailConfirm) {
        errorMessage.textContent = '';
        return true;
    }
    errorMessage.textContent = '- Emails do not match';
    return false;
}

function passwordMatch() {
    let password = document.getElementById('password').value;
    let passwordConfirm = document.getElementById('verifyPassword').value;
    let errorMessage = document.getElementById('verify-password-error-message');
    if (password === passwordConfirm) {
        errorMessage.textContent = '';
        return true;
    }
    errorMessage.textContent = '- Passwords do not match';
    return false;
}

function passwordValidation() {
    let is_valid = true;
    let password = document.getElementById('password').value;
    let errorMessage = document.getElementById('password-error-message');
    errorMessage.innerHTML = '';
    if (password.length < 8) {
        let span = document.createElement('span');
        span.textContent = '- Password must be at least 8 characters';
        errorMessage.appendChild(span);
        errorMessage.appendChild(document.createElement('br'));
        is_valid = false;
    }
    if (!password.match(/[a-z]/)) {
        let span = document.createElement('span');
        span.textContent = '- Password must contain at least one lowercase letter';
        errorMessage.appendChild(span);
        errorMessage.appendChild(document.createElement('br'));
        is_valid = false;
    }
    if (!password.match(/[A-Z]/)) {
        let span = document.createElement('span');
        span.textContent = '- Password must contain at least one uppercase letter';
        errorMessage.appendChild(span);
        errorMessage.appendChild(document.createElement('br'));
        is_valid = false;
    }
    if (!password.match(/[0-9]/)) {
        let span = document.createElement('span');
        span.textContent = '- Password must contain at least one number';
        errorMessage.appendChild(span);
        errorMessage.appendChild(document.createElement('br'));
        is_valid = false;
    }
    if (!password.match(/[^a-zA-Z\d]/)) {
        let span = document.createElement('span');
        span.textContent = '- Password must contain at least one special character';
        errorMessage.appendChild(span);
        errorMessage.appendChild(document.createElement('br'));
        is_valid = false;
    }
    return is_valid;
}

export function getRegisterPage() {
    fetch('public/html/register-form.html')
    .then(response => response.text())
    .then(template => {
        document.getElementById('main').innerHTML = template;
        document.getElementById('loginLink').addEventListener('click', function(event) {
            event.preventDefault();
            router('login');
        });
        document.querySelector('.card-body').addEventListener('submit', function(event) {
            event.preventDefault()
            let error = 0;
            if (!emailMatch()) {
                error = 1;
            }
            if (!passwordValidation()) {
                error = 1;
            }
            if (!passwordMatch()) {
                error = 1;
            }
            if (error) {
                return;
            }
            let usr_email = document.getElementById('email').value;
            let usr_password = document.getElementById('password').value;
            let usr_username = document.getElementById('name').value;
            fetch(api_url + 'auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: usr_username,
                    email: usr_email,
                    password: usr_password,
                }),
            })
            .then(response => {
                if (response.status === 201) {
                    router('login');
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    console.log("Error: " + data)
                }
            })
            .catch(error => console.log(error));
        });
    });
}