import { getTournamentList, getTournamentOwnedList } from "./getPlay.js";
import { addPrevNextButtons } from "../profile/profileUtils.js";
import { router } from "../main.js";
import { createJoinButton, tounamentContext, createDeleteButton } from "./getUtils.js";

export async function injectTournamentList(page = 1) {
  const tournaments = await getTournamentList(page);
  const tournamentListContainer = document.getElementById("tournament_list");
  tournamentListContainer.innerHTML = "";

  await tournaments.results.forEach(async (tournament) => {
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
    `;
      li.innerHTML = tournamentContent;
      tournamentListContainer.appendChild(li);
      await createJoinButton(tournament, li, tournament.is_joined);
    }
  });
  addPrevNextButtons(tournaments, tournamentListContainer, tounamentContext);
}

async function attachLinkListener() {
  const tournamentLinks = document.querySelectorAll(".tournament-link");
  tournamentLinks.forEach((link) => {
    link.addEventListener("click", () => {
      const uid = link.getAttribute("data-uid");
      router("/tournament/" + uid);
    });
  });
}

export async function injectJoinedTournamentList() {
  try {
    const tournaments = await getTournamentList(0);
    const tournamentsListContainer = document.getElementById(
      "tournament_joined_list_own"
    );
    tournamentsListContainer.innerHTML = "";

    await tournaments.results.forEach(async (tournament) => {
      if (!tournament.is_owner) {
        const li = document.createElement("li");
        li.classList.add(
          "list-group-item",
          "d-flex",
          "align-items-center",
          "justify-content-between"
        );

        const tournamentJoinedContent = `
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px;">
              <h5 style="text-align: left" class="tournament-link" data-uid="${tournament.uid}"><strong>${tournament.name}</strong></h5>
              <span>Places restantes: ${tournament.place_left}</span>
              <span>${tournament.is_active ? "En cours" : "en attente..."}</span>
            </div>
          `;
        li.innerHTML = tournamentJoinedContent;
        tournamentsListContainer.appendChild(li);
      }
    });
    attachLinkListener();
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

    await tournamentsOwned.forEach(async (tournament) => {
      const li = document.createElement("li");
      li.classList.add(
        "list-group-item",
        "d-flex",
        "align-items-center",
        "justify-content-between"
      );

      const tournamentOwnedContent = `
      <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px;">
        <h5 style="text-align: left" class="tournament-link" data-uid="${tournament.uid}"><strong>${tournament.name}</strong></h5>
        <span>Places restantes: ${tournament.place_left}</span>
        <span>${tournament.is_active ? "En cours" : "en attente..."}</span>
      </div>
        `;
      li.innerHTML = tournamentOwnedContent;
      tournamentsListContainer.appendChild(li);
    });
    attachLinkListener();
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
