import { router } from "../main.js";
import {
  fetchTemplate,
  loadProfileCss,
} from "../pageUtils.js";
import { injectTournamentList, injectJoinedTournamentList } from "./injectPlay.js";
import { attachSubmitNewTournamentListener  } from "./getUtils.js";


export async function displayPlayPage() {
  try {
    const matchmakingHtml = await fetchTemplate("/public/html/play.html");
    loadProfileCss("/public/css/play.css");
    document.getElementById("main").innerHTML = matchmakingHtml;
    await injectTournamentList();
    await injectJoinedTournamentList();
    await attachSubmitNewTournamentListener();
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}
