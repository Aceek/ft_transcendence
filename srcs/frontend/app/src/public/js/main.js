import { getLoginPage, checkOAuthCode } from "./login.js";
import { getHomePage } from "./home.js";
import { getRegisterPage } from "./register.js";
import { isAPIConnected } from "./ping.js";
import { displayProfile } from "./profile/profile.js";
import { displayFriendsProfile } from "./profile/profileFriends.js";

// export const api_url = "http://localhost:8000/api/";
export const api_url = "https://localhost/api/";

export async function router() {
  const path = window.location.pathname;

  const profileRegex = /^\/profile\/([a-zA-Z0-9_-]+)$/;
  const match = path.match(profileRegex);

  console.log(`Navigating to path: ${path}`);

  if (await isAPIConnected()) {
    if (match) {
      console.log("Loading profile page");
      const UID = match[1];
      console.log('UID:', UID)
      displayFriendsProfile(UID);
      return;
    }
    switch (path) {
      case "/home":
        console.log("Loading home page");
        getHomePage();
        break;
      case "/register":
        console.log("Loading register page");
        getRegisterPage();
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
  } else {
    console.log("User is not authenticated, loading login page");
    getLoginPage();
  }
}

router();
