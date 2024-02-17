import { api_url, router } from "../main.js";
import { fetchTemplate, loadProfileCss } from "../pageUtils.js";

export async function displayRoom() {
  try {
      const matchmakingHtml = await fetchTemplate(
        "/public/html/pong.html"
      );
      document.getElementById("main").innerHTML = matchmakingHtml;
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}
