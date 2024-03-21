import {
  verifierAliasRemplis,
  verifierNombreJoueurs,
  verifierValiditeAlias,
  verifierUniciteAlias,
} from "./verificationForm.js";
import { printConfirmationMessage } from "../profile/profileUtils.js";

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
  return true;
}
