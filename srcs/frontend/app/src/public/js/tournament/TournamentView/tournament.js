import { router } from "../../main.js";
import { fetchTemplate, loadProfileCss } from "../../pageUtils.js";
import { getTournamentByUID } from "../getTournament.js";
import { injectTournamentInfo, injectUsersInTournament, injectMatchsInTournament, injectWinner } from "./injectTournament.js";
import { attachRefreshButtonListener } from "../getUtils.js";

export async function displayTournamentPage(tournamentUID) {
  try {
    const tournamentHtml = await fetchTemplate("/public/html/tournament.html");
    loadProfileCss("/public/css/tournament.css");
    document.getElementById("main").innerHTML = tournamentHtml;
    const tournament = await getTournamentByUID(tournamentUID);
    await injectTournamentInfo(tournament);
    await injectUsersInTournament(tournament);
    await injectMatchsInTournament(tournament, tournament.round);
    await injectWinner(tournament);
    await attachRefreshButtonListener(tournament.uid);
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}
