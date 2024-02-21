import { printConfirmationMessage } from "../profile/profileUtils.js";
import { getDataWithToken, deleteDataWithToken } from "../pageUtils.js";
import { api_url } from "../main.js";
import {
  injectTournamentList,
  injectJoinedOrOwnTournamentList,
} from "./TournamentAll/injectTournament.js";
import { postData } from "../pageUtils.js";
import { joinedOrOwnedActive } from "./TournamentAll/allTournament.js";

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
    await joinTournament(tournament.uid, createOrLeave);
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

export async function joinTournament(tournamentUID, createOrLeave = false) {
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
      printConfirmationMessage(errorResponse.message, "tournament_list", "red");
      console.log("response", errorResponse.message);
      throw new Error(errorResponse.message);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function deleteTournament(tournamentUID) {
  const url = `${api_url}play/tournaments/${tournamentUID}/delete`;
  try {
    let response = await deleteDataWithToken(url);
    if (!response.ok) {
      const errorResponse = await response.json();
      console.log("response", errorResponse.message);
      printConfirmationMessage(errorResponse.message, "tournament_list", "red");
      throw new Error(errorResponse.message);
    }
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
      const tournamentName = document.getElementById("tournament_name").value;
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
