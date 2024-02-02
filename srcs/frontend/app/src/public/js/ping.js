import { api_url } from './main.js';
import { remove_url_parameter } from './url.js';

export async function isAPIConnected() {
    var accessToken = localStorage.getItem('accessToken');
    if (accessToken == null) {
        return Promise.resolve(false);
    }
    return fetch(api_url + 'auth/ping/', {
        headers: {
            'Authorization': 'Bearer ' + accessToken
        }
    })
    .then(response => {
        if (response.status === 200) {
            remove_url_parameter();
            return true;
        } else {
            if (localStorage.getItem('refreshToken') == null) {
                return false;
            }
            return fetch(api_url + 'auth/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh: localStorage.getItem('refreshToken'),
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.access) {
                    localStorage.setItem('accessToken', data.access);
                    remove_url_parameter();
                    return true;
                } else {
                    return false;
                }
            })
        }
    })
    .catch(error => {
        console.error('Error:', error);
        return false;
    });
}
