import {
  addEventListenerById,
  loadProfileCss,
  fetchTemplate,
} from "../pageUtils.js";
import { router } from "../main.js";
import { handleMatchmaking } from "../matchmaking/matchmaking.js";

async function addEventListeners() {
  addEventListenerById("play-button", "click", async function (event) {
    event.preventDefault();
    await handleMatchmaking("2");
  });
}

export async function getHomePage() {
  try {
    const homeHtml = await fetchTemplate("/public/html/home.html");
    document.getElementById("main").innerHTML = homeHtml;
    loadProfileCss("/public/css/home.css");
    await addEventListeners();
  } catch (error) {
    console.error("Error fetching home.html:", error);
    router("/home");
  }
}
