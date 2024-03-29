import { addAlias, launchLocalTournament } from "./utilsLocal.js";
import { router, api_url } from "../main.js";
import { deleteDataWithToken } from "../pageUtils.js";

export async function addEventListenersNbPlayers() {
  const nbPlayers = document.getElementById("nbPlayers");
  nbPlayers.addEventListener("input", async () => {
    if (nbPlayers.value > 8) {
      nbPlayers.value = 8;
    }
    addAlias();
  });
}

export async function addEventListenersLanchLocalTournament() {
  const lanchLocalTournament = document.getElementById("lanchLocalTournament");
  lanchLocalTournament.addEventListener("click", async () => {
    await launchLocalTournament();
  });
}

export function addEventListenersJoinAndDeleteLocalTournament() {
  document
    .getElementById("joinLocalTournament")
    .addEventListener("click", () => {
      router("/local/tournament");
    });
  document
    .getElementById("deleteLocalTournament")
    .addEventListener("click", async () => {
      const response = await deleteDataWithToken(
        api_url + "play/tournaments/local"
      );
      if (response.ok) {
        router("/local");
      } else {
        console.error("Erreur lors de la suppression du tournoi local");
      }
    });
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
}

export function addEventListenerLaunchLocalGame() {
  document.getElementById("launchLocalGame").addEventListener("click", () => {
    console.log("Launching standard offline game");

    const uuid = generateUUID();

    router(`/pong/offline/2/standard/${uuid}/`);
  });
}
