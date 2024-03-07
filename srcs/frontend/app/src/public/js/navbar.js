import { fetchTemplate, loadProfileCss } from "./pageUtils.js";
import { router, credentialsOption, api_url } from "./main.js";
import { getProfile } from "./profile/getProfile.js";
import { handleMatchmaking } from "./matchmaking/matchmaking.js";

export async function injectNavBar() {
  if (document.getElementById("navbar")) {
    return;
  }
  try {
    loadProfileCss("/public/css/navbar.css");
    const navbarDivString = await fetchTemplate("/public/html/navbar.html");
    document.body.insertAdjacentHTML("afterbegin", navbarDivString);
    const profile = await getProfile();
    injectAvatarOnNavbar(profile);
    addEventListenerToNavLinks();
    await addEventListenerToMatchamking();
    const logoutLink = document.getElementById("logout-link");
    logoutLink.addEventListener("click", handleLogout);
    window.addEventListener("hashchange", updateActiveLink);
    window.addEventListener("popstate", updateActiveLink);
  } catch (error) {
    console.error("Error in injectNavBar:", error);
  }
}

export function collapseNavbarIfExpanded() {
  const navbarCollapse = document.getElementById("navbarNavDropdown");
  const navbarToggler = document.querySelector(".navbar-toggler");
  const isExpanded = navbarToggler.getAttribute("aria-expanded") === "true";

  if (isExpanded) {
    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
      toggle: false,
    });
    bsCollapse.hide();
  }
}

async function addEventListenerToNavLinks() {
  const navLinks = document.querySelectorAll(".active-link");
  navLinks.forEach((link) => {
    if (!link.hasEventListener) {
      link.hasEventListener = true;
      link.addEventListener("click", (event) => {
        event.preventDefault();
        const path = link.getAttribute("href");
        collapseNavbarIfExpanded();
        router(path);
      });
    }
  });
}

function injectAvatarOnNavbar(profile) {
  const avatar = document.getElementById("navbarAvatar");
  avatar.src = profile.avatar || "/public/images/profile.jpg";
}

export function updateActiveLink(currentPath = window.location.pathname) {
  const navLinks = document.querySelectorAll(".active-link");

  navLinks.forEach((link) => {
    link.classList.remove("active");

    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
}

async function handleLogout(event) {
  event.preventDefault();
  try {
    const response = await fetch(api_url + "auth/logout", {
      method: "GET",
      credentials: credentialsOption,
    });
    const response_status = response.status;
    console.log("Logout response status:", response_status);
    router("/login");
  } catch (error) {
    console.error("Error during logout:", error);
  }
}

async function addEventListenerToMatchamking() {
  const matchmakingList = document.querySelectorAll(".game-mode");

  async function lauchMatchmaking(numberOfPlayers) {
    console.log("Launching matchmaking for", numberOfPlayers, "players");
    await handleMatchmaking(numberOfPlayers);
  }

  matchmakingList.forEach(function (element) {
    element.addEventListener("click", async function (e) {
      e.preventDefault();
      const numberOfPlayers = element.getAttribute("data-mode");
      await lauchMatchmaking(numberOfPlayers);
    });
  });
}
