import { router } from "../../main.js";
import { fetchTemplate, loadProfileCss } from "../../pageUtils.js";
import {
  injectTournamentList,
  injectJoinedOrOwnTournamentList,
} from "./injectTournament.js";
import { attachSubmitNewTournamentListener, ReffreshButtonListener } from "../getUtils.js";

export let joinedOrOwnedActive = true;

export async function displayPlayPage() {
  try {
    const matchmakingHtml = await fetchTemplate("/public/html/tournamentAll.html");
    loadProfileCss("/public/css/tournamentsAll.css");
    document.getElementById("main").innerHTML = matchmakingHtml;

    await ReffreshButtonListener();
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
