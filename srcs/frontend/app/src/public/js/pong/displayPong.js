import { router } from "../main.js";
import { fetchTemplate, loadProfileCss, loadScript } from "../pageUtils.js";
import { setupGame } from "./main.js";

export async function getPongGamePage() {

  try {
    const pongHtml = await fetchTemplate("/public/html/pong.html");
    document.getElementById("main").innerHTML = pongHtml;
    loadProfileCss("/public/css/pong.css");
  
    await loadScript("/public/js/pong/main.js").then(async() => {
        await setupGame();
    });
  
  } catch (error) {
    console.error("Error fetching pong.html:", error);
    router("/home");
  }
}

