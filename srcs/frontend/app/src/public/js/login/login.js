import { router, api_url, credentialsOption } from "../main.js";
import {
  fetchTemplate,
  addEventListenerById,
  addEventListenerByClass,
  postData,
  changeUrlHistory,
  deleteNavbar,
  addEventListenerByIdPreventDouble
} from "../pageUtils.js";

async function fetch42AuthLink() {
  try {
    const response = await fetch(api_url + "auth/oauth2/", {
      method: "GET",
    });
    const data = await response.json();
    return data.authorization_url;
  } catch (error) {
    console.error("Error:", error);
  }
}

function getFormData() {
  let usr_email = document.getElementById("emailField").value;
  let usr_password = document.getElementById("passwordField").value;
  return { email: usr_email, password: usr_password };
}

async function handleLoginResponse(response) {
  let errorMessage = document.getElementById("error-message");
  document.getElementById('info-message').textContent = '';
  if (response.status === 200) {
    errorMessage.textContent = "";
    let data = null;
    try {
      data = await response.json();
      if (data && '2FA' in data) {
        sessionStorage.setItem("2fa_token", data['2FA']);
        router("/2fa");
      }
    } catch (error) {
      router("/home");
    }
  } else if (response.status === 401) {
    errorMessage.textContent = "Invalid email or password";
  } else {
    errorMessage.textContent = "An error occurred. Please try again later.";
  }
}

function addEventListeners() {
  addEventListenerByIdPreventDouble("registerLink", "click", function (event) {
    router("/register");
  });
  addEventListenerByIdPreventDouble("42button", "click", async function (event) {
    window.location.href = await fetch42AuthLink();
  });
  addEventListenerByIdPreventDouble("loginForm", "submit", async function (event) {
    let formData = getFormData();
    let response = await postData(api_url + "auth/login/", formData);
    handleLoginResponse(response);
  });
}

export async function getLoginPage() {
  try {
    const template = await fetchTemplate("/public/html/login-form.html");
    document.getElementById("main").innerHTML = template;
    if (sessionStorage.getItem('register') === 'true') {
      document.getElementById('info-message').textContent = 'Account successfully created, please validate your email before login in.';
      sessionStorage.removeItem('register');
    }
    else if (sessionStorage.getItem('validate') === 'true') {
      document.getElementById('info-message').textContent = 'Email successfully validated, you can now login !';
      sessionStorage.removeItem('validate');
    }
    addEventListeners();
  } catch (error) {
    console.error(error);
  }
}

export async function checkEmailVerification() {
  const urlParams = new URLSearchParams(window.location.search);
  const uid = urlParams.get("uid");
  const token = urlParams.get("token");

  if (uid && token) {
    return fetch(api_url + "mail/validate/" + `?uid=${uid}&token=${token}`, {
      method: "GET",
      credentials: credentialsOption,
    })
      .then((response) => {
        return response.status === 200;
      })
      .catch((error) => {
        console.error(error);
        return false;
      });
  }
  return Promise.resolve(false);
}

export async function checkOAuthCode() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");

  if (!code) {
    return { success: false, requires2FA: false };
  }
  changeUrlHistory("/");
  const response = await fetch(api_url + "auth/oauth2/" + `?code=${code}`, {
    method: "GET",
    credentials: credentialsOption,
  });
  if (response.ok) {
    try {
      const data = await response.json();
      if (data && '2FA' in data) {
        sessionStorage.setItem("2fa_token", data['2FA']);
        return { success: true, requires2FA: true };
      }
    } catch (error) {
      return { success: true, requires2FA: false };
    }
  }
  return { success: false, requires2FA: false };
}
