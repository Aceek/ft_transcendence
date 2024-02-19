import { printConfirmationMessage } from "../profile/profileUtils.js";
import { getDataWithToken, deleteDataWithToken } from "../pageUtils.js";
import { api_url } from "../main.js";
import {
  injectTournamentList,
  injectJoinedTournamentList,
} from "./injectPlay.js";
import { postData } from "../pageUtils.js";

export const tounamentContext = {
  currentPage: 1,
  updatePage: function (page) {
    this.currentPage = page;
    injectTournamentList(this.currentPage);
  },
};

export async function createJoinButton(tournament, li, createOrLeave = false) {
  try {
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
      await injectJoinedTournamentList();
    });
    li.appendChild(joinButton);
    return joinButton;
  } catch (error) {
    console.log("Error:", error);
  }
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
      throw new Error(errorResponse.message);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

// export async function attachSubmitNewTournamentListener() {
//   try {
//     const submitNewTournament = document.getElementById(
//       "submit_new_tournament"
//     );
//     submitNewTournament.addEventListener("click", async () => {
//       const tournamentName = document.getElementById("tournament_name").value;
//       const numberOfPlayers =
//         document.getElementById("number-of-players").value;
//       const url = `${api_url}play/tournaments`;
//       data = {};
//       data.name = tournamentName;
//       data.max_participants = numberOfPlayers;
//       const response = postData(url, data);
//       if (response.status === 201) {
//         printConfirmationMessage("Tournament created", "number-of-players");
//         await injectTournamentList(tounamentContext.currentPage);
//       } else {
//         const errorResponse = await response.json();
//         printConfirmationMessage(
//           errorResponse.message,
//           "number-of-players",
//           "red"
//         );
//       }
//     });
//   } catch (error) {
//     console.error("Error:", error);
//   }
// }
