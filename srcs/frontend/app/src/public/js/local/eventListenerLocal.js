import { launchLocalTournament } from "./displayLocal.js";
import { addAlias } from "./utilsLocal.js";

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
