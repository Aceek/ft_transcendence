import { credentialsOption } from "./main.js";

export function addEventListenerById(id, event, handler) {
  document.getElementById(id).addEventListener(event, handler);
}

export function addEventListenerByClass(className, event, handler) {
  document.querySelector(className).addEventListener(event, handler);
}

export async function fetchTemplate(url) {
  const response = await fetch(url);
  return await response.text();
}

export async function postData(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    credentials: credentialsOption,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response;
}

export async function requestDataWithToken(url = "", data, method = "GET") {
  const headers = new Headers({
    "Content-Type": "application/json",
  });

  let requestOptions = {
    method: method,
    headers: headers,
    credentials: credentialsOption,
  };

  if (
    (method === "POST" || method === "PATCH" || method === "PUT") &&
    !(data instanceof FormData)
  ) {
    requestOptions.body = JSON.stringify(data);
  } else if (data instanceof FormData) {
    headers.delete("Content-Type");
    requestOptions.body = data;
    console.log("requestOptions", requestOptions);
  }

  try {
    const response = await fetch(url, requestOptions);
    return response;
  } catch (error) {
    console.error("Erreur lors de la requête:", error.message);
    throw error;
  }
}

export async function getDataWithToken(url = "") {
  const response = await fetch(url, {
    method: "GET",
    credentials: credentialsOption,
  });
  return response;
}

export async function deleteDataWithToken(url = "") {
  const response = await fetch(url, {
    method: "DELETE",
    credentials: credentialsOption,
  });
  return response;
}

export function fieldsMatch(
  fieldId1,
  fieldId2,
  errorMessageId,
  errorMessageText
) {
  let field1 = document.getElementById(fieldId1).value;
  let field2 = document.getElementById(fieldId2).value;
  let errorMessage = document.getElementById(errorMessageId);
  if (field1 === field2) {
    errorMessage.textContent = "";
    return true;
  }
  errorMessage.textContent = errorMessageText;
  return false;
}

export function setTokensStorage(data) {
  localStorage.setItem("refreshToken", data.refresh);
  localStorage.setItem("accessToken", data.access);
}

export function loadProfileCss(url) {
  const head = document.head;
  const existingLink = Array.from(head.querySelectorAll("link")).find((link) =>
    link.href.includes(url)
  );

  if (!existingLink) {
    const link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = url;
    link.id = "CssFromPageSPA";

    head.appendChild(link);
  }
}

export function delProfileCss(url){
  const head = document.head;
  const existingLink = Array.from(head.querySelectorAll("link")).find((link) =>
    link.href.includes(url)
  );
  if (existingLink) {
    existingLink.remove();
  }
}

export function changeUrlHistory(pathname) {
  const url = new URL(window.location.href);
  url.pathname = pathname;
  url.search = "";
  history.pushState({}, "", url);
}

export function loadScript(url) {
  return new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${url}"]`);
    if (existingScript) {
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.src = url;
    script.type = "module"; // Added to dynammically import module in pong game
    script.onload = resolve;
    script.onerror = reject;
    document.body.appendChild(script);
  });
}

export function deleteNavbar() {
  if (document.getElementById('navbar')) {
    document.getElementById('navbar').remove();
  }
}

export function addEventListenerByIdPreventDouble(id, eventType, callback) {
  const element = document.getElementById(id);
  addEventListenerDOMElem(element, eventType, callback);
}

export function addEventListenerDOMElem(element, eventType, callback) {
  if (element) {
    if (!element.dataset.listenerAdded) {
        element.addEventListener(eventType, async (event) => {
            event.preventDefault();
            if (callback.constructor.name === "AsyncFunction") {
                await callback(event);
            } else {
                callback(event);
            }
        });
        element.dataset.listenerAdded = "true";
    }
  } else {
    console.error(`Element not found`);
  }
}
