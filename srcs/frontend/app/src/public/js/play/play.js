import { api_url, router } from "../main.js";
import { loadScript, fetchTemplate, loadProfileCss } from "../pageUtils.js";

export async function displayPlayPage() {
  try {
    const matchmakingHtml = await fetchTemplate(
      "/public/html/play.html"
    );
    loadProfileCss("/public/css/profile.css");
    document.getElementById("main").innerHTML = matchmakingHtml;
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}