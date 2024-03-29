import { router, api_url } from "./main.js";
import {
  addEventListenerById,
  addEventListenerByClass,
  fetchTemplate,
  postData,
  fieldsMatch,
  changeUrlHistory,
  addEventListenerByIdPreventDouble
} from "./pageUtils.js";

function emailMatch() {
  return fieldsMatch(
    "email",
    "verifyEmail",
    "verify-email-error-message",
    "- Emails do not match",
  );
}

function passwordMatch() {
  return fieldsMatch(
    "password",
    "verifyPassword",
    "verify-password-error-message",
    "- Passwords do not match",
  );
}

function displayRegistrationError(errorTag, msg) {
  let span = document.createElement("span");
  span.textContent = `${msg}`;
  errorTag.appendChild(span);
  errorTag.appendChild(document.createElement("br"));
  return false;
}

function passwordValidation() {
  let is_valid = true;
  let password = document.getElementById("password").value;
  let errorTag = document.getElementById("password-error-message");
  errorTag.innerHTML = "";
  if (password.length < 8) {
    is_valid = displayRegistrationError(
      errorTag,
      "- Password must be at least 8 characters",
    );
  }
  if (!password.match(/[a-z]/)) {
    is_valid = displayRegistrationError(
      errorTag,
      "- Password must contain at least one lowercase letter",
    );
  }
  if (!password.match(/[A-Z]/)) {
    is_valid = displayRegistrationError(
      errorTag,
      "- Password must contain at least one uppercase letter",
    );
  }
  if (!password.match(/[0-9]/)) {
    is_valid = displayRegistrationError(
      errorTag,
      "- Password must contain at least one number",
    );
  }
  if (!password.match(/[^a-zA-Z\d]/)) {
    is_valid = displayRegistrationError(
      errorTag,
      "- Password must contain at least one special character",
    );
  }
  return is_valid;
}

function validateForm() {
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
    return false;
  }
  return true;
}

function getFormData() {
  let usr_email = document.getElementById("email").value;
  let usr_password = document.getElementById("password").value;
  let usr_username = document.getElementById("name").value;
  return { username: usr_username, email: usr_email, password: usr_password };
}

async function handleResponse(response) {
  let errorEmailTag = document.getElementById("email-error-message");
  let errorUsernameTag = document.getElementById("username-error-message");
  errorEmailTag.innerHTML = "";
  errorUsernameTag.innerHTML = "";
  if (response.status === 201) {
    sessionStorage.setItem('register', 'true');
    router("/login");
  } else if (response.status === 400) {
    try {
      const data = await response.json();
      if (data) {
        if (data.email) {
          errorEmailTag.innerHTML = data.email;
        }
        if (data.username) {
          errorUsernameTag.innerHTML = data.username;
        }
      }
    } catch (error) {
      console.log("No data in response");
    }
  }
}

function addEventListeners() {
  addEventListenerByIdPreventDouble("loginLink", "click", (event) => {
    router("/login");
  });
  addEventListenerByIdPreventDouble("registerForm", "submit", async (event) => {
    if (!validateForm()) {
      return;
    }
    let formData = getFormData();
    let response = await postData(api_url + "auth/register/", formData);
    handleResponse(response);
  });
}

export async function getRegisterPage() {
  try {
    const template = await fetchTemplate("/public/html/register-form.html");
    document.getElementById("main").innerHTML = template;
    addEventListeners();
  } catch (error) {
    console.error("Error:", error);
  }
}
