const api_url = 'http://localhost:8000/api/';

async function fetchContent(url) {
    const response = await fetch(url);
    const content = await response.json();
    return content;
}


function getLoginPage() {
    fetch('static/html/login-form.html')
        .then(response => response.text())
        .then(template => {
            document.getElementById('main').innerHTML = template;
        });
    console.log(fetchContent(api_url + 'auth/oauth2/'));
}

getLoginPage();

