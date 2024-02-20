import { router } from "../main.js";
import { fetchTemplate, loadProfileCss } from "../pageUtils.js";
import {
  injectTournamentList,
  injectJoinedOrOwnTournamentList,
} from "./injectPlay.js";
import { attachSubmitNewTournamentListener } from "./getUtils.js";

export let joinedOrOwnedActive = true;

export async function displayPlayPage() {
  try {
    const matchmakingHtml = await fetchTemplate("/public/html/play.html");
    loadProfileCss("/public/css/play.css");
    document.getElementById("main").innerHTML = matchmakingHtml;
    await injectTournamentList();
    await injectJoinedOrOwnTournamentList(true);
    await handleInjectJoinOrOwnTournament();
    await attachSubmitNewTournamentListener();
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

async function handleInjectJoinOrOwnTournament() {
  const joinTournamentButton = document.getElementById(
    "joined_tournament_button"
  );
  joinTournamentButton.addEventListener("click", async () => {
    joinedOrOwnedActive = true;
    await injectJoinedOrOwnTournamentList(true);
  });

  const ownTournamentButton = document.getElementById(
    "owner_tournament_button"
  );
  ownTournamentButton.addEventListener("click", async () => {
    joinedOrOwnedActive = false;
    await injectJoinedOrOwnTournamentList(false);
  });
}
