import { getLoginPage, checkOAuthCode, checkEmailVerification } from "./login.js";
import { getHomePage } from "./home/home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./networkUtils.js";
import { displayProfile } from "./profile/profile.js";
import { displayFriendsProfile } from "./profile/profileFriends.js";
import { displayStats } from "./profile/stats/stats.js";
import { injectNavBar, updateActiveLink } from "./navbar.js";
import { displayMatchmaking } from "./matchmaking/matchamking.js";
import { getPongGamePage } from "./pong/displayPong.js";
import { deleteNavbar } from "./pageUtils.js";
import { displayPlayPage } from "./tournament/TournamentAll/tournamentAll.js";
import { displayTournamentPage } from "./tournament/TournamentView/tournament.js";
import { get2FAPage } from "./2fa.js";

let portString = window.location.port ? ":" + window.location.port : "";
export const api_url = "https://" + window.location.hostname + portString + "/api/";

export const credentialsOption = "include";
window.addEventListener("popstate", (event) => {
  router(window.location.pathname, false);
});

export function clearLoadedCss() {
  const head = document.head;
  const links = Array.from(head.querySelectorAll("link"));
  links.forEach((link) => {
    if (link.href.includes("profile.css")) {
      head.removeChild(link);
    }
    if (link.href.includes("tournament.css")) {
      head.removeChild(link);
    }
    if (link.href.includes("tournamentsAll.css")) {
      head.removeChild(link);
    }
    if (link.href.includes("chat.css")) {
      head.removeChild(link);
    }
    if (link.href.includes("2fa.css")) {
      head.removeChild(link);
    }
  });
}

export async function router(path, updateHistory = true) {
  if (!path) {
    path = window.location.pathname;
  }

  console.log(`Navigating to path: ${path}`);

  if (updateHistory) {
    history.pushState(null, "", path + window.location.search);
  }

  clearLoadedCss();

  if (await checkEmailVerification()) {
    sessionStorage.setItem('validate', 'true');
  }

  if (await isAPIConnected()) {
    await injectNavBar();
    handleAuthenticatedRoutes(path);
  } else {
    handleUnauthenticatedRoutes(path);
  }
}

async function matchRegex(path) {
  const profileMatch = path.match(/^\/profile\/(?!stats$)([a-zA-Z0-9_-]+)$/);
  const profileStatsMatch = path.match(/^\/profile\/([a-zA-Z0-9_-]+)\/stats$/);
  const pongMatch = path.match(/^\/pong\/([a-zA-Z0-9_-]+)$/);
  const tournamentMatch = path.match(/^\/tournament\/([a-zA-Z0-9_-]+)$/);

  if (profileStatsMatch) {
    const UID = profileStatsMatch[1];
    console.log("Loading profile stats page with UID:", UID);
    await displayStats(UID);
    return true;
  } else if (profileMatch) {
    const UID = profileMatch[1];
    console.log("Loading profile page with UID:", UID);
    await displayFriendsProfile(UID);
    return true;
  } else if (pongMatch) {
    const pongID = pongMatch[1];
    console.log("Loading room page with roomID:", pongID);
    await getPongGamePage(pongID);
    return true;
  } else if (tournamentMatch) {
    const tournamentID = tournamentMatch[1];
    await displayTournamentPage(tournamentID);
    return true;
  }
  return false;
}

async function handleAuthenticatedRoutes(path) {
  sessionStorage.removeItem('validate');
  if (await matchRegex(path)) {
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
      case "/matchmaking":
        console.log("Loading matchmaking page");
        await displayMatchmaking();
        break;
      case "/play":
        console.log("Loading play page");
        await displayPlayPage();
        break;
      default:
        path = "/home";
        console.log("Path not found, loading default page");
        getHomePage();
    }
  }
  updateActiveLink(path);
}

async function handleUnauthenticatedRoutes(path) {
  deleteNavbar();
  if (await checkOAuthCode()) {
    console.log("User has OAuth code, redirecting to home page");
    router("/home");
  } else if (path === "/register") {
    console.log("Loading register page");
    getRegisterPage();
  } else if (path === "/2fa") {
    console.log("Loading 2fa page");
    get2FAPage();
  } else {
    path = "/login";
    console.log("Loading login page");
    getLoginPage();
  }
}

router();
