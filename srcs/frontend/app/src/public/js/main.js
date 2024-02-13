import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./ping.js";
import { displayProfile } from "./profile/profile.js";
import { displayFriendsProfile } from "./profile/profileFriends.js";

// export const api_url = "http://localhost:8000/api/";
export const api_url = "https://localhost/api/";

// Fonction principale pour le routage
export async function router(path) {
  
  if (!path) {
    path = window.location.pathname;
  }
  console.log(`Navigating to path: ${path}`);

  if (await isAPIConnected()) {
    handleAuthenticatedRoutes(path);
  } else {
    handleUnauthenticatedRoutes(path);
  }
}

// Gère les routes pour les utilisateurs authentifiés
async function handleAuthenticatedRoutes(path) {
  const profileMatch = path.match(/^\/profile\/([a-zA-Z0-9_-]+)$/);

  if (profileMatch) {
    const UID = profileMatch[1];
    console.log("Loading profile page with UID:", UID);
    displayFriendsProfile(UID);
  } else {
    switch (path) {
      case "/home":
        console.log("Loading home page");
        getHomePage();
        break;
      case "/profile":
        console.log("Loading personal profile page");
        displayProfile();
        break;
      default:
        console.log("Path not found, loading default page");
        getHomePage();
    }
  }
}

// Gère les routes pour les utilisateurs non authentifiés
async function handleUnauthenticatedRoutes(path) {
  if (await checkOAuthCode()) {
    console.log("User has OAuth code, redirecting to home page");
    router("/home");
  } else if (path === "/register") {
    console.log("Loading register page");
    getRegisterPage();
  } else {
    console.log("Loading login page");
    getLoginPage();
  }
}

router();
