import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./networkUtils.js";
import { displayProfile } from "./profile/profile.js";

// export const api_url = "http://localhost:8000/api/";
export const api_url = "https://localhost/api/";

export const credentialsOption = "include";

export async function router(path) {
  if (!path) {
    path = window.location.pathname;
  }
  console.log(`Navigating to path: ${path}`);
  if (await isAPIConnected()) {
    switch (path) {
      case "/home":
        getHomePage();
        break;
      case "/profile":
        console.log("Loading profile page");
        displayProfile();
        break;
      default:
        console.log("Loading default page");
        getHomePage();
        break;
    }
  } else if (await checkOAuthCode()) {
    console.log("User has OAuth code, redirecting to home page");
    router("/home");
    return;
  } else if (path === "/register") {
    getRegisterPage();
  } else {
    console.log("User is not authenticated, loading login page");
    getLoginPage();
  }
}

router();
