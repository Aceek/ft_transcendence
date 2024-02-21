import { fetchTemplate, loadProfileCss } from "./pageUtils.js";
import { router, credentialsOption, api_url } from "./main.js";
import { getProfile } from "./profile/getProfile.js";

export async function injectNavBar() {
  loadProfileCss("/public/css/navbar.css");
  if (document.getElementById("navbar")) {
    console.log("La barre de navigation est déjà chargée.");
    return;
  }
  try {
    const navbarDivString = await fetchTemplate("/public/html/navbar.html");
    document.body.insertAdjacentHTML("afterbegin", navbarDivString);
    const profile = await getProfile();
    injectAvatarOnNavbar(profile);
    addEventListenerToNavLinks();
    const logoutLink = document.getElementById('logout-link');
    logoutLink.addEventListener('click', handleLogout);
    window.addEventListener("hashchange", updateActiveLink);
    window.addEventListener("popstate", updateActiveLink);
  } catch (error) {
    console.error("Error in injectNavBar:", error);
  }
}

async function addEventListenerToNavLinks() {
  const navLinks = document.querySelectorAll(".active-link");

  navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const path = link.getAttribute("href");
      router(path);
    });
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
    const response = await fetch(api_url + 'auth/logout', {
      method: 'GET',
      credentials: credentialsOption,
    });
    const response_status = response.status;
    console.log('Logout response status:', response_status);
    router('/login');
  } catch (error) {
    console.error('Error during logout:', error);
  }
}
