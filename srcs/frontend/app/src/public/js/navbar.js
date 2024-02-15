import { fetchTemplate } from "./pageUtils.js";
import { router } from "./main.js";

export async function injectNavBar() {
  if (document.getElementById("navbar")) {
    console.log("La barre de navigation est déjà chargée.");
    return;
  }
  try {
    const navbarDivString = await fetchTemplate("/public/html/navbar.html");
    document.body.insertAdjacentHTML("afterbegin", navbarDivString);
    addEventListenerToNavLinks();
    updateActiveLink();
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
      updateActiveLink(path);
      router(path);
    });
  });
}

function updateActiveLink(currentPath = window.location.pathname) {
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    link.classList.remove("active");

    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
}
