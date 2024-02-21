import {
  getTournamentList,
  getTournamentOwnedList,
  getTournamentHistory,
} from "../getTournament.js";
import { addPrevNextButtons, attachLinkListenerProfile } from "../../profile/profileUtils.js";
import { router } from "../../main.js";
import {
  createJoinButton,
  tounamentContext,
  createDeleteButton,
} from "../getUtils.js";
import { getProfile} from "../../profile/getProfile.js";

export async function injectTournamentList(page = 1) {
  try {
    const tournaments = await getTournamentList(page);
    const tournamentListContainer = document.getElementById("tournament_list");
    tournamentListContainer.innerHTML = "";

    await Promise.all(
      tournaments.results.map(async (tournament) => {
        if (!tournament.is_finished) {
          const li = document.createElement("li");
          li.classList.add(
            "list-group-item",
            "d-flex",
            "align-items-center",
            "justify-content-between",
            "li-item"
          );
          const tournamentContent = `
          <h5 style="text-align: left" class="tournament-name">${tournament.name}</h5>
          <span>Places: ${tournament.place_left}</span>
          <span>${tournament.is_active ? "En cours" : "en attente..."}</span>
          <span>${tournament.is_owner ? "Créateur" : ""}</span>
        `;
          li.innerHTML = tournamentContent;
          tournamentListContainer.appendChild(li);
          if (!tournament.is_owner) {
            await createJoinButton(tournament, li, tournament.is_joined);
          }
        }
      })
    );
    addPrevNextButtons(tournaments, tournamentListContainer, tounamentContext);
  } catch (error) {
    console.error("Error:", error);
  }
}

async function attachLinkListenerTournament() {
  const tournamentLinks = document.querySelectorAll(".tournament-link");
  tournamentLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", () => {
        const uid = link.getAttribute("data-uid");
        router("/tournament/" + uid);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}

export async function injectJoinedTournamentList() {
  try {
    const tournaments = await getTournamentList(0);
    const tournamentsListContainer = document.getElementById(
      "tournament_joined_list_own"
    );
    tournamentsListContainer.innerHTML = "";

    tournaments.results.forEach((tournament) => {
      if (!tournament.is_owner) {
        const li = document.createElement("li");
        li.classList.add(
          "list-group-item",
          "d-flex",
          "align-items-center",
          "justify-content-between"
        );

        const tournamentJoinedContent = `
          <h5 style="text-align: left" class="tournament-link" data-uid="${tournament.uid}"><strong>${tournament.name}</strong></h5>
          <span>Places: ${tournament.place_left}</span>
          <span>${tournament.is_active ? "En cours" : "en attente..."}</span>
          `;
        li.innerHTML = tournamentJoinedContent;
        tournamentsListContainer.appendChild(li);
      }
    });
    attachLinkListenerTournament();
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function injectOwnedTournamentList() {
  try {
    const tournamentsOwned = await getTournamentOwnedList();
    const tournamentsListContainer = document.getElementById(
      "tournament_joined_list_own"
    );
    tournamentsListContainer.innerHTML = "";

    await Promise.all(
      tournamentsOwned.map(async (tournament) => {
        const li = document.createElement("li");
        li.classList.add(
          "list-group-item",
          "d-flex",
          "align-items-center",
          "justify-content-between"
        );

        const tournamentOwnedContent = `
        <h5 style="text-align: left" class="tournament-link tournament-name" data-uid="${tournament.uid}"><strong>${tournament.name}</strong></h5>
        <span style="margin-right: 15px;">Places: ${tournament.place_left}</span>
        <span style="margin-right: 15px;">${tournament.is_active ? "En cours" : "en attente..."}</span>
        `;
        li.innerHTML = tournamentOwnedContent;
        tournamentsListContainer.appendChild(li);
        await createDeleteButton(tournament, li);
      })
    );
    attachLinkListenerTournament();
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function injectJoinedOrOwnTournamentList(joined = true) {
  if (joined) {
    const joinTournamentButton = document.getElementById(
      "joined_tournament_button"
    );
    joinTournamentButton.classList.add("active");
    const ownTournamentButton = document.getElementById(
      "owner_tournament_button"
    );
    ownTournamentButton.classList.remove("active");
    await injectJoinedTournamentList();
  } else {
    const joinTournamentButton = document.getElementById(
      "joined_tournament_button"
    );
    joinTournamentButton.classList.remove("active");
    const ownTournamentButton = document.getElementById(
      "owner_tournament_button"
    );
    ownTournamentButton.classList.add("active");
    await injectOwnedTournamentList();
  }
}

export async function injectTournamentHistory() {
  try {
    const tournaments = await getTournamentHistory();
    const tournamentsListContainer = document.getElementById(
      "tournament_history_list"
    );
    
    tournamentsListContainer.innerHTML = "";
    
    for (const tournament of tournaments) {
      const winner = await getProfile(tournament.winner);
      const li = document.createElement("li");
      li.classList.add(
        "list-group-item",
        "d-flex",
        "align-items-center",
        "justify-content-between",
        "li-item"
      );
      const tournamentContent = `
        <h5 style="text-align: left" class="tournament-link" data-uid="${tournament.uid}"><strong>${tournament.name}</strong></h5>
        <span class="profile-link" data-uid="${winner.id}"><strong>${winner.username}</strong></span>
      `;
      li.innerHTML = tournamentContent;
      tournamentsListContainer.appendChild(li);
    }
    attachLinkListenerTournament();
    attachLinkListenerProfile();
  } catch (error) {
    console.error("Error:", error);
  }
}
