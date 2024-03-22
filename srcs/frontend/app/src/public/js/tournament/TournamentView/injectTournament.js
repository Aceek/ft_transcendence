import { attachLinkListenerProfile } from "../../profile/profileUtils.js";
import { launchTournament } from "../getUtils.js";
import { deleteTournament } from "../getUtils.js";
import { getProfile } from "../../profile/getProfile.js";
import {
  createJoinOrLeaveButton,
  createUsersDiv,
  createMatchDiv,
} from "../getUtils.js";
import { router } from "../../main.js";
import { displayTournamentPage } from "./tournament.js";

export async function injectWinner(tournament) {
  if (tournament.is_finished && tournament.winner) {
    const winner = await getProfile(tournament.winner);
    // create container for winner
    const winnerContainer = document.createElement("div");
    winnerContainer.className = "winner-container";
    winnerContainer.innerHTML = `
    <div id="tournament_winner_row" class="row gutters-sm">
      <div id="tournament_winner_col">
        <div class="card mb-3">
          <div class="card-body">
            <h6 class="d-flex align-items-center mb-3">Gagnant</h6>
            <div class="d-flex flex-column align-items-center text-center">
              <img src="${winner.avatar || "/public/images/profile.jpg"}" alt="Avatar de ${winner.username}" class="rounded-circle" width="150">
              <h4>${winner.username}</h4>
            </div>
                
          </div>
        </div>
      </div>
    </div>
    `;
    const matchesContainer = document.getElementById("matches_tournament_div");
    matchesContainer.parentNode.insertBefore(winnerContainer, matchesContainer);
  }
}

export async function injectRoundButtons(tournament, funct = createMatchDiv) {
  const rounds = [...new Set(tournament.matches.map((match) => match.round))];
  const buttonsContainer = document.getElementById(
    "tournament_match_round_button_col"
  );
  buttonsContainer.innerHTML = "";

  rounds.forEach((round) => {
    const button = document.createElement("button");
    button.classList.add("btn", "btn-primary");
    button.style.marginLeft = "10px";

    if (tournament.is_finished) {
      button.textContent = `Round ${round}`;
    } else {
      button.textContent =
        round === tournament.round
          ? `Round ${round} en cours`
          : `Round ${round}`;
    }

    button.addEventListener("click", () =>
      injectMatchsInTournament(tournament, round, funct)
    );
    buttonsContainer.appendChild(button);
  });
}

export async function injectTournamentInfo(tournament) {
  if (!tournament) {
    console.error("Les informations du tournoi ne sont pas disponibles.");
    return;
  }

  // Mettez à jour le contenu de chaque élément avec les données de l'API
  try {
    const ownerUser = await getProfile(tournament.ownerUser);
    document.getElementById("tournament_owner").textContent =
      `Propriétaire : ${ownerUser.username}`;
  } catch (error) {
    console.error("Error:", error);
  }
  document.getElementById("tournament_name").textContent = tournament.name;
  document.getElementById("tournament_created_at").textContent =
    `Créé le : ${new Date(tournament.created_at).toLocaleDateString()}`;
  document.getElementById("tournament_is_active").textContent =
    `Actif : ${tournament.is_active ? "Oui" : "Non"}`;
  document.getElementById("tournament_is_finished").textContent =
    `Terminé : ${tournament.is_finished ? "Oui" : "Non"}`;
  document.getElementById("tournament_is_joined").textContent =
    `Rejoint : ${tournament.is_joined ? "Oui" : "Non"}`;
  document.getElementById("tournament_max_participants").textContent =
    `Participants max : ${tournament.max_participants}`;
  document.getElementById("tournament_place_left").textContent =
    `Places restantes : ${tournament.place_left}`;
  document.getElementById("tournament_round").textContent =
    `Round : ${tournament.round}`;

  if (!tournament.is_owner) {
    await createJoinOrLeaveButton(
      tournament,
      tournament.is_joined ? true : false
    );
  }
  await createDeleteButtonIfOwner(tournament);
  await createLaunchButtonIfOwner(tournament);
}

export async function injectUsersInTournament(tournament) {
  try {
    const users = tournament.user;

    const usersContainer = document.getElementById("tournament_users_list");
    usersContainer.innerHTML = "";
    await Promise.all(
      users.map(async (user) => {
        user = await getProfile(user);
        const userDiv = createUsersDiv(user);
        usersContainer.appendChild(userDiv);
      })
    );
    await attachLinkListenerProfile();
  } catch (error) {
    console.error("Error:", error);
  }
}

export async function injectMatchsInTournament(tournament, round, funct = createMatchDiv) {
  if (!tournament.matches) {
    console.log("No matches available");
    return;
  }
  const matchesContainer = document.getElementById("matches_tournament");
  matchesContainer.innerHTML = "";
  await Promise.all(
    tournament.matches
      .filter((match) => match.round === round)
      .map(async (match) => {
        const matchDiv = await funct(match);
        matchesContainer.appendChild(matchDiv);

        if (
          match.ready_to_play &&
          !match.is_finished &&
          !tournament.is_finished &&
          !match.is_in_game
        ) {
          await injectPlayButton(match, matchesContainer);
        }
      })
  );
  await injectRoundButtons(tournament, funct);
}

export async function injectPlayButton(match, matchDiv) {
  const playButton = document.createElement("button");
  playButton.classList.add("btn", "btn-primary");
  if (match.player1 && match.player2) {
    playButton.textContent = `${match.player1} vs ${match.player2}`;
    playButton.style = "margin-top: 10px";
  } else {
    playButton.textContent = "Rejoindre votre match";
  }

  playButton.addEventListener("click", async () => {
    router(match.room_url);
  });
  matchDiv.insertBefore(playButton, matchDiv.firstChild);
}

async function createLaunchButtonIfOwner(tournament) {
  if (tournament.is_owner && tournament.is_active === false) {
    const launchButton = document.createElement("button");
    launchButton.classList.add("btn", "btn-primary");
    launchButton.textContent = "Lancer";
    launchButton.style = "margin-left: 10px";
    launchButton.addEventListener("click", async () => {
      if (await launchTournament(tournament.uid, "functional_button_div")) {
        await displayTournamentPage(tournament.uid);
      }
    });
    const containerToAppend = document.getElementById("functional_button_div");
    containerToAppend.appendChild(launchButton);
  }
}


export async function createDeleteButtonIfOwner(tournament) {
  if (tournament.is_owner) {
    const deleteButton = document.createElement("button");
    deleteButton.classList.add("btn", "btn-danger");
    deleteButton.textContent = "Supprimer";
    deleteButton.style = "margin-left: 10px";
    deleteButton.addEventListener("click", async () => {
      if (await deleteTournament(tournament.uid, "functional_button_div")) {
        await router("/tournamentAll");
      }
    });
    const containerToAppend = document.getElementById("functional_button_div");
    containerToAppend.appendChild(deleteButton);
  }
}
