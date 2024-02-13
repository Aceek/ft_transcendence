import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./ping.js";
import { displayProfile } from "./profile/profile.js";
import { displayStats } from "./profile/stats/stats.js";
import { displayFriendsProfile } from "./profile/profileFriends.js";

// export const api_url = "http://localhost:8000/api/";
export const api_url = "https://localhost/api/";

// function updateHistoryState(path, state = {}) {
//   history.pushState(state, null, path);
// }

// window.onload = () => {
//   router(); // Gère le chargement initial de la page
// };
// window.addEventListener('popstate', (event) => {
//   // Utilisez event.state pour déterminer l'état de l'application et afficher la vue appropriée
//   router(window.location.pathname);
// });

// Fonction principale pour le routage
export async function router(path) {
  
  if (!path) {
    path = window.location.pathname;
  }
  console.log(`Navigating to path: ${path}`);
  // updateHistoryState(path);

  if (await isAPIConnected()) {
    handleAuthenticatedRoutes(path);
  } else {
    handleUnauthenticatedRoutes(path);
  }
}

// Gère les routes pour les utilisateurs authentifiés
async function handleAuthenticatedRoutes(path) {
  const profileMatch = path.match(/^\/profile\/([a-zA-Z0-9_-]+)$/);
  // const statsMatch = path.match(/^\/profile\/([a-zA-Z0-9_-]+)\/stats$/);

  if (profileMatch) {
    const UID = profileMatch[1];
    console.log("Loading profile page with UID:", UID);
    displayFriendsProfile(UID);
  // } else if (statsMatch) {
  //   const UID = statsMatch[1];
  //   console.log("Loading stats page with UID:", UID);
  //   displayStats(UID);
  } else {
    switch (path) {
      case "/home":
        console.log("Loading home page");
        getHomePage();
        break;
      case "/profile":
        console.log("Loading personal profile page");
        displayProfile();
      // case "/profile/stats":
      //   console.log("Loading personal stats page");
      //   displayStats();
      //   break;
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
