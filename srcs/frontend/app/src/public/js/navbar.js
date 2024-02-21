import { fetchTemplate, loadProfileCss } from "./pageUtils.js";
import { router } from "./main.js";
import { getProfile } from "./profile/getProfile.js";

export async function injectNavBar() {
  loadProfileCss("/public/css/navbar.css");
  if (document.getElementById("navbar")) {
    return;
  }
  try {
    const navbarDivString = await fetchTemplate("/public/html/navbar.html");
    document.body.insertAdjacentHTML("afterbegin", navbarDivString);
    const profile = await getProfile();
    injectAvatarOnNavbar(profile);
    addEventListenerToNavLinks();
    window.addEventListener("hashchange", updateActiveLink);
    window.addEventListener("popstate", updateActiveLink);
  } catch (error) {
    console.error("Error in injectNavBar:", error);
  }
}

async function addEventListenerToNavLinks() {
  const navLinks = document.querySelectorAll(".nav-link");

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
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    link.classList.remove("active");

    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
}
