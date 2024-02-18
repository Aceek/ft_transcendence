import {
  changeUrlHistory,
  addEventListenerById,
  loadProfileCss,
  fetchTemplate,
} from "../pageUtils.js";
import { router } from "../main.js";

function addEventListeners() {
  addEventListenerById("play-button", "click", function (event) {
    event.preventDefault();
    router("/pong");
  });
}

export async function getHomePage() {
  try {
    const homeHtml = await fetchTemplate("/public/html/home.html");
    document.getElementById("main").innerHTML = homeHtml;
    loadProfileCss("/public/css/home.css");
    addEventListeners();
    changeUrlHistory("/home");
  } catch (error) {
    console.error("Error fetching home.html:", error);
    router("/home");
  }
}
