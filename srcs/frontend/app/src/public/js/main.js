import {
  getLoginPage,
  checkOAuthCode,
  checkEmailVerification,
} from "./login/login.js";
import { getHomePage } from "./home/home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./networkUtils.js";
import { displayProfile } from "./profile/profile.js";
import { displayFriendsProfile } from "./profile/profileFriends.js";
import { displayStats } from "./profile/stats/stats.js";
import { injectNavBar, updateActiveLink } from "./navbar.js";
import { getPongGamePage } from "./pong/displayPong.js";
import { deleteNavbar } from "./pageUtils.js";
import { displayTournamentAllPage } from "./tournament/TournamentAll/tournamentAll.js";
import { displayTournamentPage } from "./tournament/TournamentView/tournament.js";
import { get2FAPage } from "./2fa/2fa.js";
import { clearTournamentConversationsMessages } from "./chat/tournamentChat.js";
import { handleUserActivity } from "./user_activity_websocket/user_activity_modal.js";
import { closeUserActivitySocket } from "./user_activity_websocket/user_activity_utils.js";
import { display404 } from "./display404.js";
import {
  chatSocket,
  displayChatPage,
  resetCurrentFriendId,
} from "./chat/chat.js";
import { pongSocket } from "./pong/main.js";
import { displayLocalPage } from "./local/displayLocal.js";
import { displayLocalTournamentPage } from "./tournament/localTournament.js/displayLocalTournament.js";

let portString = window.location.port ? ":" + window.location.port : "";
export const api_url =
  "https://" + window.location.hostname + portString + "/api/";

export const credentialsOption = "include";
window.addEventListener("popstate", (event) => {
  router(window.location.pathname, false);
});

export function closeChatWebSocket(path) {
  if (
    chatSocket &&
    chatSocket.readyState === WebSocket.OPEN &&
    path !== "/chat"
  ) {
    chatSocket.close();
    resetCurrentFriendId();
  }
}

export function closePongWebSocket() {
  if (pongSocket && pongSocket.readyState === WebSocket.OPEN) {
    pongSocket.close();
  }
}

export function clearLoadedCss() {
  const head = document.head;
  const links = Array.from(head.querySelectorAll("link"));
  links.forEach((link) => {
    if (link.id === "CssFromPageSPA" && !link.href.includes("navbar.css")) {
      head.removeChild(link);
    }
  });
}

function resetDataForReloadingPage(path) {
  closeChatWebSocket(path);
  closePongWebSocket();
  clearLoadedCss();
  clearTournamentConversationsMessages();
}

export async function router(path, updateHistory = true) {
  if (!path) {
    path = window.location.pathname;
  }

  console.log(`Navigating to path: ${path}`);

  if (updateHistory) {
    history.pushState(null, "", path + window.location.search);
  }

  resetDataForReloadingPage(path);

  if (await checkEmailVerification()) {
    sessionStorage.setItem("validate", "true");
  }

  if (await isAPIConnected()) {
    await injectNavBar();
    await handleUserActivity();
    handleAuthenticatedRoutes(path);
  } else {
    closeUserActivitySocket();
    handleUnauthenticatedRoutes(path);
  }
}

async function matchRegex(path) {
  const uuidPattern =
    "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";

  const profileMatch = path.match(/^\/profile\/(?!stats$)([a-zA-Z0-9_-]+)$/);
  const profileStatsMatch = path.match(/^\/profile\/([a-zA-Z0-9_-]+)\/stats$/);
  const tournamentMatch = path.match(/^\/tournament\/([a-zA-Z0-9_-]+)$/);
  
  // pong routes
  const onlineStandardMatch = path.match(new RegExp(`^/pong/online/([2-4])/standard/(${uuidPattern})/?$`));
  const onlineTournamentMatch = path.match(new RegExp(`^/pong/online/2/tournament/(${uuidPattern})/?$`));
  const offlineStandardMatch = path.match(new RegExp(`^/pong/offline/2/standard/(${uuidPattern})/?$`));
  const offlineTournamentMatch = path.match(new RegExp(`^/pong/offline/2/tournament/(${uuidPattern})/?$`));

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
  } else if (tournamentMatch) {
    const tournamentID = tournamentMatch[1];
    await displayTournamentPage(tournamentID);
    return true;
  } else if (onlineStandardMatch || onlineTournamentMatch ||
            offlineStandardMatch || offlineTournamentMatch) {
    console.log("Loading pong game:");
    await getPongGamePage();
    return true;
  }
  return false;
}

async function handleAuthenticatedRoutes(path) {
  sessionStorage.removeItem("validate");
  if (await matchRegex(path)) {
  } else {
    switch (path) {
      case "/":
      case "/home":
        await getHomePage();
        break;
      case "/profile/stats":
        console.log("Loading personal profile stats page");
        await displayStats();
        break;
      case "/profile":
        console.log("Loading personal profile page");
        await displayProfile();
        break;
      case "/tournamentAll":
        console.log("Loading tournamentAll page");
        await displayTournamentAllPage();
        break;
      case "/chat":
        await displayChatPage();
        console.log("Loading chat page");
        break;
      case "/local":
        await displayLocalPage();
        console.log("Loading local play page");
        break;
      case "/local/tournament":
        await displayLocalTournamentPage();
        console.log("Loading local tournament page");
        break;
      
      default:
        console.log("Path not found, loading default page");
        await display404();
    }
  }
  updateActiveLink(path);
}

async function handleUnauthenticatedRoutes(path) {
  deleteNavbar();
  const oauth = await checkOAuthCode();

  if (oauth.success) {
    if (oauth.requires2FA) {
      console.log("User has OAuth code, redirecting to 2fa page");
      router("/2fa");
    } else {
      console.log("User has OAuth code, redirecting to home page");
      router("/home");
    }
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
