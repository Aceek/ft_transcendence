import {
  loadProfileCss,
  fetchTemplate,
  getDataWithToken,
  deleteDataWithToken,
} from "../../pageUtils.js";
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
    injectLocalWinner(tournament);
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

    await createDeleteLocalButton(tournament);
}


export async function createDeleteButtonIfOwner(tournament) {
  if (tournament.is_owner) {
    const deleteButton = document.createElement("button");
    deleteButton.classList.add("btn", "btn-danger");
    deleteButton.textContent = "Supprimer";
    deleteButton.style = "margin-left: 10px";
    deleteButton.addEventListener("click", async () => {
      if (await deleteTournament(tournament.uid, "functional_button_div")) {
        await router("/tournamentAll");
      }
    });
    const containerToAppend = document.getElementById("functional_button_div");
    containerToAppend.appendChild(deleteButton);
  }
}

export async function deleteLocalTournament(tournamentUID) {
  const url = `${api_url}play/tournaments/local`;
  const response = await deleteDataWithToken(url);
  if (!response.ok) {
    console.error("Erreur lors de la suppression du tournoi local");
    return false;
  }
  return true;
}

export async function createDeleteLocalButton(tournament) {
  const deleteButton = document.createElement("button");
  deleteButton.classList.add("btn", "btn-danger");
  deleteButton.textContent = "Supprimer";
  deleteButton.style = "margin-left: 10px";
  deleteButton.addEventListener("click", async () => {
    if (await deleteLocalTournament(tournament.uid)) {
      await router("/local");
    }
  });
  const containerToAppend = document.getElementById("functional_button_div");
  containerToAppend.appendChild(deleteButton);
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
      <span>${match.user1}</span>
    </div>
    <div class="match__vs">VS</div>
    <div class="match__player">
      <span>${match.user2}</span>
    </div>
  `;
  return matchDiv;
}


export async function injectLocalWinner(tournament) {
  if (tournament.is_finished && tournament.winner) {
    const winner = tournament.winner;
    const winnerContainer = document.createElement("div");
    winnerContainer.className = "winner-container";
    winnerContainer.innerHTML = `
    <div id="tournament_winner_row" class="row gutters-sm">
      <div id="tournament_winner_col">
        <div class="card mb-3">
          <div class="card-body">
            <h6 class="d-flex align-items-center mb-3">Gagnant</h6>
            <div class="d-flex flex-column align-items-center text-center">
              <h4>${winner}</h4>
            </div>
                
          </div>
        </div>
      </div>
    </div>
    `;
    const matchesContainer = document.getElementById("matches_tournament_div");
    matchesContainer.parentNode.insertBefore(winnerContainer, matchesContainer);
  }
}