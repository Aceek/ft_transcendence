import { loadProfileCss, fetchTemplate } from "../pageUtils.js";
import {
  addEventListenersNbPlayers,
  addEventListenersLanchLocalTournament,
} from "./eventListenerLocal.js";
import { makeVerificationsLocal } from "./utilsLocal.js";
import { postData } from "../pageUtils.js";

export async function displayLocalPage() {
  try {
    loadProfileCss("/public/css/local.css");
    const localHtml = await fetchTemplate("/public/html/local.html");
    document.getElementById("main").innerHTML = localHtml;
    await manageCreationLocalTournament();
  } catch (error) {
    console.error("Error:", error);
    router("/home");
  }
}

export async function manageCreationLocalTournament() {
  await addEventListenersNbPlayers();
  await addEventListenersLanchLocalTournament();
}

export function prepareDataForLocalTournament() {
  const nombreJoueurs = document.getElementById("nbPlayers").value;
  const alias = [];
  for (let i = 1; i <= nombreJoueurs; i++) {
    alias.push(document.getElementById(`joueur${i}`).value);
  }
  return { nombreJoueurs, alias };
}

export async function launchLocalTournament() {
  if (!makeVerificationsLocal()) {
    return;
  }
  console.log("Toutes les vérifications sont passées. Lancement du tournoi...");
  await sendTournamentData();
}

async function sendTournamentData() {
  if (!makeVerificationsLocal()) {
    return;
  }
  const data = prepareDataForLocalTournament();
  const response = await postData("/api/tournament/local", data);
  if (response.ok) {
    console.log("Tournoi créé avec succès");
  } else {
    console.error("Erreur lors de la création du tournoi");
  }
}
