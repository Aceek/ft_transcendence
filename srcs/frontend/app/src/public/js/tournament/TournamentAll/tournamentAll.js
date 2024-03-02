import { router } from "../../main.js";
import { fetchTemplate, loadProfileCss } from "../../pageUtils.js";
import {
  injectTournamentList,
  injectJoinedOrOwnTournamentList,
  injectTournamentHistory,
} from "./injectTournamentAll.js";
import {
  attachSubmitNewTournamentListener,
  ReffreshButtonListener,
} from "../getUtils.js";

export let joinedOrOwnedActive = true;

export async function displayTournamentAllPage() {
  try {
    const matchmakingHtml = await fetchTemplate(
      "/public/html/tournamentAll.html"
    );
    loadProfileCss("/public/css/tournamentsAll.css");
    document.getElementById("main").innerHTML = matchmakingHtml;

    await ReffreshButtonListener();
    await injectTournamentList();
    await injectJoinedOrOwnTournamentList(true);
    await handleInjectJoinOrOwnTournament();
    await attachSubmitNewTournamentListener();
    await preventEnterSubmit();
    await injectTournamentHistory();
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

async function preventEnterSubmit() {
  document
    .getElementById("tournament_name_input")
    .addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
      }
    });
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
