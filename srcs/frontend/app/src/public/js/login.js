import { router, api_url, credentialsOption } from "./main.js";
import {
  fetchTemplate,
  addEventListenerById,
  addEventListenerByClass,
  postData,
  setTokensStorage,
} from "./pageUtils.js";

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

function handleLoginResponse(response) {
  let errorMessage = document.getElementById("error-message");
  if (response.status === 200) {
    errorMessage.textContent = "";
    router("/home");
  } else if (response.status === 401) {
    errorMessage.textContent = "Invalid email or password";
  } else {
    errorMessage.textContent = "An error occurred. Please try again later.";
  }
}

function addEventListeners() {
  addEventListenerById("registerLink", "click", function (event) {
    event.preventDefault();
    router("/register");
  });
  addEventListenerById("42button", "click", async function (event) {
    event.preventDefault();
    window.location.href = await fetch42AuthLink();
  });
  addEventListenerByClass(".card-body", "submit", async function (event) {
    event.preventDefault();
    let formData = getFormData();
    let response = await postData(api_url + "auth/login/", formData);
    handleLoginResponse(response);
  });
}

export async function getLoginPage() {
  try {
    const template = await fetchTemplate("public/html/login-form.html");
    document.getElementById("main").innerHTML = template;
    addEventListeners();
  } catch (error) {
    console.error(error);
  }
}

export async function checkOAuthCode() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");

  if (code) {
    urlParams.delete("code");
    urlParams.delete;
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.history.replaceState({}, document.title, newUrl);
    return fetch(api_url + "auth/oauth2/" + `?code=${code}`, {
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
