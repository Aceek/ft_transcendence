import { router } from "../main.js";
import { fetchTemplate, loadProfileCss, loadScript } from "../pageUtils.js";
import { setupGame } from "./main.js";

export async function getPongGamePage(pongID) {
  console.log("Pong.js is loading!");

  try {
    const pongHtml = await fetchTemplate("/public/html/pong.html");
    document.getElementById("main").innerHTML = pongHtml;
    loadProfileCss("/public/css/pong.css");
  
    console.log("about to load script");
    await loadScript("/public/js/pong/main.js").then(() => {
        console.log("should have loaded the script");
        setupGame(); // Call setupGame here after main.js is loaded
    });
  
  } catch (error) {
    console.error("Error fetching pong.html:", error);
    router("/home");
  }
}

