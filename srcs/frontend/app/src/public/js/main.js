import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./ping.js";

export const api_url = "http://localhost:8000/api/";

export async function router(path) {
  if (!path) {
    path = window.location.pathname;
  }
  if (await isAPIConnected()) {
    switch (path) {
      case "/home":
        getHomePage();
        break;
      default:
        getHomePage();
        break;
    }
  } else if (await checkOAuthCode()) {
    router("/home");
    return;
  } else if (path === "/register") {
    getRegisterPage();
  } else {
    getLoginPage();
  }
}

router();
