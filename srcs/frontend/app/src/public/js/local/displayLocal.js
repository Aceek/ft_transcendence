import { loadProfileCss, fetchTemplate } from "../pageUtils.js";
import {
  addEventListenersNbPlayers,
  addEventListenersLanchLocalTournament,
} from "./eventListenerLocal.js";
import { makeVerificationsLocal } from "./utilsLocal.js";
import { postData } from "../pageUtils.js";
import { api_url, router } from "../main.js";
import { printConfirmationMessage } from "../profile/profileUtils.js";
import { extractErrorMessages } from "../tournament/getUtils.js";
import { getDataWithToken, deleteDataWithToken } from "../pageUtils.js";


export async function injectCreateLocalTournament() {
  const createLocalTournament = document.getElementById("createLocalTournament");
  createLocalTournament.innerHTML = `
    <h2>Créer un tournoi</h2>
    <div class="mb-3">
      <label for="nbPlayers" class="form-label">Nombre de joueurs</label>
      <input type="number" class="form-control" id="nbPlayers" required max="8">
    </div>
    <div id="joueursAlias"></div>
    <button id="lanchLocalTournament" type="button" class="btn btn-warning">Lancer le tournoi</button>
  `;
}


export async function displayLocalPage() {
  try {
    loadProfileCss("/public/css/local.css");
    const localHtml = await fetchTemplate("/public/html/local.html");
    document.getElementById("main").innerHTML = localHtml;
    if (!await verifyifLocalTournament()) {
      await injectCreateLocalTournament();
      await manageCreationLocalTournament();
    } else {
      injectJoinAndDeleteLocalTournament();
    }
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

export function addEventListenersJoinAndDeleteLocalTournament() {
  document.getElementById("joinLocalTournament").addEventListener("click", () => {
    router("/local/tournament");
  });
  document.getElementById("deleteLocalTournament").addEventListener("click", async () => {
    const response = await deleteDataWithToken(api_url + "play/tournaments/local");
    if (response.ok) {
      router("/local");
    } else {
      console.error("Erreur lors de la suppression du tournoi local");
    }
  }
  );
}

export function injectJoinAndDeleteLocalTournament() {
  document.getElementById("createLocalTournament").innerHTML = "";
  const joinAndDeleteLocalTournament = document.createElement("div");
  joinAndDeleteLocalTournament.id = "joinAndDeleteLocalTournament";
  joinAndDeleteLocalTournament.innerHTML = `
    <button id="joinLocalTournament" class="btn btn-primary">Rejoindre le tournoi local</button>
    <button id="deleteLocalTournament" class="btn btn-danger">Supprimer le tournoi local</button>
  `;
  document.getElementById("createLocalTournament").appendChild(joinAndDeleteLocalTournament);
  addEventListenersJoinAndDeleteLocalTournament();

}

export async function verifyifLocalTournament() {
  const response = await getDataWithToken(api_url + "play/tournaments/local");
  if (response.ok) {
    const data = await response.json();
    if (data.length > 0) {
      return true;
    }
  }
  return false;
}


export async function manageCreationLocalTournament() {
  await addEventListenersNbPlayers();
  await addEventListenersLanchLocalTournament();
}

export function prepareDataForLocalTournament() {
  const nombreJoueurs = document.getElementById("nbPlayers").value;
  const participants = [];
  for (let i = 1; i <= nombreJoueurs; i++) {
    participants.push(document.getElementById(`joueur${i}`).value);
  }
  return { nombreJoueurs, participants };
}

export async function launchLocalTournament() {
  if (!makeVerificationsLocal()) {
    return;
  }
  await sendTournamentData();
}

async function sendTournamentData() {
  if (!makeVerificationsLocal()) {
    return;
  }
  const data = prepareDataForLocalTournament();
  const response = await postData(api_url + "play/tournaments/local", data);
  if (response.ok) {
    router("/local/tournament");
  } else {
    const errorMessage = extractErrorMessages(await response.json());
    printConfirmationMessage(errorMessage, "joueursAlias", "red")
  }
}
