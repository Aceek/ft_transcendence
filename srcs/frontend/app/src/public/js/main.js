const api_url = 'http://localhost:8000/api/';

async function fetchContent(url) {
    const response = await fetch(url);
    const content = await response.json();
    return content;
}


function getLoginPage() {
    fetch('public/html/login-form.html')
        .then(response => response.text())
        .then(template => {
            document.getElementById('main').innerHTML = template;
        });
    //console.log(fetchContent(api_url + 'auth/oauth2/'));
}

function getPongGamePage() {
    fetch('public/html/pong.html')
        .then(response => response.text())
        .then(template => {
            document.getElementById('main').innerHTML = template;

            // Load Pong script after injecting the Pong game HTML
            const script = document.createElement('script');
            script.src = 'public/js/pong.js';
            document.head.appendChild(script);
        });
}

// getLoginPage();
getPongGamePage();
console.log('main.js was executed!');

