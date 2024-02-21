import { printConfirmationMessage } from "../profile/profileUtils.js";
import { getDataWithToken, deleteDataWithToken } from "../pageUtils.js";
import { api_url } from "../main.js";
import {
  injectTournamentList,
  injectJoinedOrOwnTournamentList,
} from "./TournamentAll/injectTournamentAll.js";
import { postData } from "../pageUtils.js";
import { joinedOrOwnedActive } from "./TournamentAll/tournamentAll.js";
import { displayTournamentPage } from "./TournamentView/tournament.js";
import { getProfile } from "../profile/getProfile.js";

export const tounamentContext = {
  currentPage: 1,
  updatePage: function (page) {
    this.currentPage = page;
    injectTournamentList(this.currentPage);
  },
};

export async function createJoinButton(tournament, li, createOrLeave = false) {
  let text = "Rejoindre";
  let btnClass = "btn-primary";
  if (createOrLeave) {
    text = "Quitter";
    btnClass = "btn-danger";
  }
  const joinButton = document.createElement("button");
  joinButton.classList.add("btn", btnClass);
  joinButton.textContent = text;
  joinButton.addEventListener("click", async () => {
    await joinOrLeaveTournament(
      tournament.uid,
      createOrLeave,
      "tournament_list"
    );
    await injectTournamentList(tounamentContext.currentPage);
    await injectJoinedOrOwnTournamentList(joinedOrOwnedActive);
  });

  li.appendChild(joinButton);
  return joinButton;
}

export async function createDeleteButton(tournament, containerToAppend) {
  const deleteButton = document.createElement("button");
  deleteButton.classList.add("btn", "btn-danger");
  deleteButton.textContent = "Supprimer";
  deleteButton.addEventListener("click", async () => {
    await deleteTournament(tournament.uid);
    await injectTournamentList(tounamentContext.currentPage);
    await injectJoinedOrOwnTournamentList(joinedOrOwnedActive);
  });
  containerToAppend.appendChild(deleteButton);
  return deleteButton;
}

export async function launchTournament(tournamentUID, containerNameToAppend) {
  const url = `${api_url}play/tournaments/${tournamentUID}/launch`;
  let response = null;
  try {
    response = await getDataWithToken(url);
    if (!response.ok) {
      const errorResponse = await response.json();
      printConfirmationMessage(
        errorResponse.message,
        containerNameToAppend,
        "red"
      );
      return false;
    }
    return true;
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function joinOrLeaveTournament(
  tournamentUID,
  createOrLeave = false,
  containerNameToAppend
) {
  const url = `${api_url}play/tournaments/${tournamentUID}/join`;
  let response = null;
  try {
    if (!createOrLeave) {
      response = await getDataWithToken(url);
    } else {
      response = await deleteDataWithToken(url);
    }
    if (!response.ok) {
      const errorResponse = await response.json();
      printConfirmationMessage(
        errorResponse.message,
        containerNameToAppend,
        "red"
      );
      return false;
    }
    return true;
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function deleteTournament(
  tournamentUID,
  containerNameToError = "tournament_list"
) {
  const url = `${api_url}play/tournaments/${tournamentUID}/delete`;
  try {
    let response = await deleteDataWithToken(url);
    if (!response.ok) {
      const errorResponse = await response.json();
      console.log("response", errorResponse.message);
      printConfirmationMessage(
        errorResponse.message,
        containerNameToError,
        "red"
      );
      return false;
    }
    return true;
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function attachSubmitNewTournamentListener() {
  try {
    const submitNewTournament = document.getElementById(
      "submit_new_tournament"
    );
    submitNewTournament.addEventListener("click", async () => {
      const tournamentName = document.getElementById(
        "tournament_name_input"
      ).value;
      const numberOfPlayers =
        document.getElementById("number-of-players").value;
      const url = `${api_url}play/tournaments`;
      let data = {};
      data = {
        name: tournamentName,
        max_participants: numberOfPlayers,
      };

      const response = await postData(url, data);
      if (response.status === 201) {
        printConfirmationMessage("Tournament created", "number-of-players");
        await injectTournamentList(tounamentContext.currentPage);
        await injectJoinedOrOwnTournamentList(joinedOrOwnedActive);
      } else {
        const reponseJson = await response.json();
        console.log("Json = ", reponseJson);
        const errorResponse = extractErrorMessages(reponseJson);
        printConfirmationMessage(errorResponse, "number-of-players", "red");
      }
    });
  } catch (error) {
    console.error("Error:", error);
  }
}

function extractErrorMessages(errors) {
  let errorMessages = "";

  if (Array.isArray(errors)) {
    errorMessages = errors.join(", ");
  } else {
    Object.keys(errors).forEach((field) => {
      const messages = errors[field].join(", ");
      errorMessages += `${field}: ${messages}\n`;
    });
  }

  return errorMessages.trim();
}

export async function ReffreshButtonListener() {
  const refreshButton = document.getElementById("refresh_button");
  refreshButton.addEventListener("click", async () => {
    await injectTournamentList(tounamentContext.currentPage);
  });
}

export async function createMatchDiv(match) {
  try {
    const player1 = await getProfile(match.user1);
    const player2 = await getProfile(match.user2);

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
        <span data-uid="${player1.id}">${player1.username}</span>
      </div>
      <div class="match__vs">VS</div>
      <div class="match__player">
      <span data-uid="${player2.id}">${player2.username}</span>
      </div>
    `;
    return matchDiv;
  } catch (error) {
    console.error("Error:", error);
  }
}

export function createUsersDiv(user) {
  const listItem = document.createElement("li");
  listItem.className =
    "list-group-item d-flex align-items-center justify-content-between";

  listItem.innerHTML = `
    <div class="users-tournament-info d-flex align-items-center">
      <img src="${user.avatar || "/public/images/profile.jpg"}" alt="Avatar de ${user.username}" class="rounded-circle me-3" width="75" height="75">
      <div>
        <span class="profile-link" data-uid="${user.id}"><strong>${user.username}</strong></span>
      </div>
    </div>
  `;
  return listItem;
}

export async function createJoinOrLeaveButton(
  tournament,
  createOrLeave = false
) {
  let text = "Rejoindre";
  let btnClass = "btn-primary";
  if (createOrLeave) {
    text = "Quitter";
    btnClass = "btn-danger";
  }
  const joinButton = document.createElement("button");
  joinButton.classList.add("btn", btnClass);
  joinButton.textContent = text;
  joinButton.addEventListener("click", async () => {
    if (
      await joinOrLeaveTournament(
        tournament.uid,
        createOrLeave,
        "functional_button_div"
      )
    ) {
      await displayTournamentPage(tournament.uid);
    }
  });

  const containerToAppend = document.getElementById("functional_button_div");
  containerToAppend.appendChild(joinButton);
}

export async function attachRefreshButtonListener(tournamentUID) {
  const refreshButton = document.getElementById("refresh_tournament_button");
  refreshButton.addEventListener("click", async () => {
    await displayTournamentPage(tournamentUID);
  });
}
