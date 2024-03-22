import {
  verifierAliasRemplis,
  verifierNombreJoueurs,
  verifierValiditeAlias,
  verifierUniciteAlias,
  verifySizeAlias,
} from "./verificationLocal.js";
import { printConfirmationMessage } from "../profile/profileUtils.js";
import { postData } from "../pageUtils.js";
import {
  addEventListenersNbPlayers,
  addEventListenersLanchLocalTournament,
  addEventListenersJoinAndDeleteLocalTournament,
} from "./eventListenerLocal.js";
import { router, api_url } from "../main.js";
import { extractErrorMessages } from "../tournament/getUtils.js";

export function addAlias() {
  const nombreJoueurs = document.getElementById("nbPlayers").value;
  const container = document.getElementById("joueursAlias");
  container.innerHTML = "";

  let row = document.createElement("div");
  row.className = "row";
  container.appendChild(row);

  for (let i = 1; i <= nombreJoueurs; i++) {
    if (i % 2 === 1 && i > 1) {
      row = document.createElement("div");
      row.className = "row";
      container.appendChild(row);
    }

    const col = document.createElement("div");
    col.className = "col-md-6 mb-3";

    col.innerHTML = `
      <label for="joueur${i}" class="form-label">Alias Joueur ${i}</label>
      <input type="text" class="form-control" id="joueur${i}" required>
    `;

    row.appendChild(col);
  }
}

export function makeVerificationsLocal() {
  let errorMessage = "";
  if (!verifierNombreJoueurs()) {
    errorMessage =
      "Le nombre de joueurs doit être renseigné et être supérieur ou égal à 2.";
    printConfirmationMessage(errorMessage, "joueursAlias", "red");
    return false;
  }

  if (!verifierAliasRemplis()) {
    errorMessage = "Tous les alias doivent être renseignés.";
    printConfirmationMessage(errorMessage, "joueursAlias", "red");
    return false;
  }

  if (!verifierValiditeAlias()) {
    errorMessage = "Les alias doivent être des usernames valides.";
    printConfirmationMessage(errorMessage, "joueursAlias", "red");
    return false;
  }

  if (!verifierUniciteAlias()) {
    errorMessage = "Les alias doivent être uniques.";
    printConfirmationMessage(errorMessage, "joueursAlias", "red");
    return false;
  }

  if (!verifySizeAlias()) {
    errorMessage =
      "Les alias doivent avoir une taille inférieure ou égale à 10.";
    printConfirmationMessage(errorMessage, "joueursAlias", "red");
    return false;
  }
  return true;
}

export async function sendTournamentData() {
  if (!makeVerificationsLocal()) {
    return;
  }
  const data = prepareDataForLocalTournament();
  const response = await postData(api_url + "play/tournaments/local", data);
  if (response.ok) {
    router("/local/tournament");
  } else {
    const errorMessage = extractErrorMessages(await response.json());
    printConfirmationMessage(errorMessage, "joueursAlias", "red");
  }
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

export async function manageCreationLocalTournament() {
  await addEventListenersNbPlayers();
  await addEventListenersLanchLocalTournament();
}

export function injectJoinAndDeleteLocalTournament() {
  document.getElementById("createLocalTournament").innerHTML = "";
  const joinAndDeleteLocalTournament = document.createElement("div");
  joinAndDeleteLocalTournament.id = "joinAndDeleteLocalTournament";
  joinAndDeleteLocalTournament.innerHTML = `
    <button id="joinLocalTournament" class="btn btn-primary">Rejoindre le tournoi local</button>
    <button id="deleteLocalTournament" class="btn btn-danger">Supprimer le tournoi local</button>
  `;
  document
    .getElementById("createLocalTournament")
    .appendChild(joinAndDeleteLocalTournament);
  addEventListenersJoinAndDeleteLocalTournament();
}

export async function injectCreateLocalTournament() {
  const createLocalTournament = document.getElementById(
    "createLocalTournament"
  );
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
