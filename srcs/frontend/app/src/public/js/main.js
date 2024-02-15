import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./networkUtils.js";
import { displayProfile } from "./profile/profile.js";
import { displayFriendsProfile } from "./profile/profileFriends.js";
import { displayStats } from "./profile/stats/stats.js";
import { injectNavBar } from "./navbar.js";

// export const api_url = "http://localhost:8000/api/";
export const api_url = "https://localhost/api/";

export const credentialsOption = "include";
window.addEventListener("popstate", (event) => {
  router(window.location.pathname, false);
});

export async function router(path, updateHistory = true) {
  if (!path) {
    path = window.location.pathname;
  }

  console.log(`Navigating to path: ${path}`);

  if (updateHistory) {
    history.pushState(null, "", path);
  }

  if (await isAPIConnected()) {
    await injectNavBar();
    handleAuthenticatedRoutes(path);
  } else {
    handleUnauthenticatedRoutes(path);
  }
}

async function handleAuthenticatedRoutes(path) {
  const profileMatch = path.match(/^\/profile\/(?!stats$)([a-zA-Z0-9_-]+)$/);
  const profileStatsMatch = path.match(/^\/profile\/([a-zA-Z0-9_-]+)\/stats$/);

  if (profileStatsMatch) {
    const UID = profileStatsMatch[1];
    console.log("Loading profile stats page with UID:", UID);
    await displayStats(UID);
  } else if (profileMatch) {
    const UID = profileMatch[1];
    console.log("Loading profile page with UID:", UID);
    await displayFriendsProfile(UID);
  } else {
    switch (path) {
      case "/home":
        getHomePage();
        break;
      case "/profile/stats":
        console.log("Loading personal profile stats page");
        await displayStats();
        break;
      case "/profile":
        console.log("Loading personal profile page");
        await displayProfile();
        break;
      default:
        console.log("Path not found, loading default page");
        getHomePage();
    }
  }
}

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
