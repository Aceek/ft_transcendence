import { router } from "../main.js";
import { fetchTemplate, loadProfileCss, loadScript } from "../pageUtils.js";

export async function getPongGamePage(pongID) {
  try {
    const pongHtml = await fetchTemplate("/public/html/pong.html");
    document.getElementById("main").innerHTML = pongHtml;
    loadProfileCss("/public/css/pong.css");
    loadScript("/public/js/pong/main.js");
  } catch (error) {
    console.error("Error fetching pong.html:", error);
    router("/home");
  }
}
