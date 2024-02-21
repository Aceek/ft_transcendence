import { router } from "../../main.js";
import { fetchTemplate, loadProfileCss } from "../../pageUtils.js";
import { getTournamentByUID } from "../getTournament.js";

export async function displayTournamentPage(tournamentUID) {
  try {
    const tournamentHtml = await fetchTemplate("/public/html/tournament.html");
    const tournamentCss = loadProfileCss("/public/css/tournamentsAll.css");
    document.getElementById("main").innerHTML = tournamentHtml;

    const tournament = await getTournamentByUID(tournamentUID);
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}
