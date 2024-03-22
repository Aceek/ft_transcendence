

export function verifierNombreJoueurs() {
  const nombreJoueurs = parseInt(document.getElementById("nbPlayers").value);
  return !isNaN(nombreJoueurs) && nombreJoueurs >= 2;
}

export function verifierAliasRemplis() {
  const inputsAlias = document.querySelectorAll("#joueursAlias input");
  for (let input of inputsAlias) {
    if (!input.value) {
      return false;
    }
  }
  return true;
}

export function verifierUniciteAlias() {
  const inputsAlias = document.querySelectorAll("#joueursAlias input");
  let aliasSet = new Set();

  for (let input of inputsAlias) {
    if (aliasSet.has(input.value)) {
      return false;
    }
    aliasSet.add(input.value);
  }

  return true;
}

export function verifierValiditeAlias() {
  const regexUsernameValide = /^[a-zA-Z0-9_]+$/;
  const inputsAlias = document.querySelectorAll("#joueursAlias input");
  for (let input of inputsAlias) {
    if (!regexUsernameValide.test(input.value)) {
      return false;
    }
  }
  return true;
}

export function verifySizeAlias() {
  const inputsAlias = document.querySelectorAll("#joueursAlias input");
  for (let input of inputsAlias) {
    if (input.value.length > 10) {
      return false;
    }
  }
  return true;
}