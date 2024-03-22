
import { loadProfileCss, fetchTemplate, getDataWithToken } from "../../pageUtils.js";
import { router, api_url } from "../../main.js";
import { injectMatchsInTournament } from "../TournamentView/injectTournament.js";


export async function displayLocalTournamentPage() {
  try {
    loadProfileCss("/public/css/tournament.css");
    const localHtml = await fetchTemplate("/public/html/localTournament.html");
    document.getElementById("main").innerHTML = localHtml;
    const tournament = await getLocalTournament();
    await injectLocalTournamentInfo(tournament);
    injectUserInLocalTournament(tournament);
    injectMatchsInTournament(tournament, tournament.round, createLocalMatchDiv);
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

export function injectUserInLocalTournament(tournament) {
  const users = tournament.participants;
  const usersContainer = document.getElementById("tournament_users_list");
  usersContainer.innerHTML = "";
  
  users.forEach((user) => {
    const userDiv = createLocalUsersDiv(user);
    usersContainer.appendChild(userDiv);
  });
  
}

export function createLocalUsersDiv(user) {
  const userDiv = document.createElement("div");
  userDiv.innerHTML = `
    <div class="card">
      <div class="card-body">
        <p class="card-text">${user}</p>
      </div>
    </div>
  `;
  return userDiv;
}


export async function getLocalTournament() {
  const url = `${api_url}play/tournaments/local`;
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get local tournament");
  }
  const data = await response.json();
  return data[0];
}

export async function injectLocalTournamentInfo(tournament) {
  if (!tournament) {
    console.error("Les informations du tournoi ne sont pas disponibles.");
    return;
  }

  document.getElementById("tournament_is_finished").textContent =
    `Terminé : ${tournament.is_finished ? "Oui" : "Non"}`;
  document.getElementById("tournament_round").textContent =
    `Round : ${tournament.round}`;
}


export function createLocalMatchDiv(match) {
  const status = match.is_finished ? "Terminé" : "Non terminé";
  const inGame = match.is_in_game ? "En jeu" : "";

  const matchDiv = document.createElement("div");
  matchDiv.className =
    "list-group-item d-flex align-items-center justify-content-between match";
  matchDiv.innerHTML = `
    <div class="match__info mb-2">
      <span>${status}${inGame}</span>
    </div>
    <div class="match__player">
      <span>${match.player1}</span>
    </div>
    <div class="match__vs">VS</div>
    <div class="match__player">
      <span>${match.player2}</span>
    </div>
  `;
  return matchDiv;
}