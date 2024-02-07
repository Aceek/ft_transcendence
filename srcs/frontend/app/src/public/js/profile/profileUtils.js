import { requestDataWithToken } from "../pageUtils.js";
import { getGameHistory, getFriendList } from "./getProfile.js";

export async function sendUpdateRequest(url, data, method = "PATCH") {
  try {
    const response = await requestDataWithToken(url, data, method);
    if (response.status === 200) {
      return true;
    } else {
      return false;
    }
  } catch (error) {
    console.error("Error :", error);
    return false;
  }
}

export async function injectFriendList() {
  const friendList = await getFriendList();
  const friendListContainer = document.getElementById("friendsList");
  friendListContainer.innerHTML = friendList
    .map((friend) => {
      return `
      <li class="list-group-item d-flex align-items-center">
        <img src="${friend.avatar || "../images/profile.jpg"}" alt="Avatar de ${friend.username}" class="rounded-circle me-3" width="75" height="75">
        <div>
          <strong>${friend.username}</strong>
          <span class="text-success ms-2">• En ligne</span>
        </div>
      </li>
    `;
    })
    .join("");
}

export let currentHistoryPage = 1;

export async function injectHistoryList(page) {
  const historyList = await getGameHistory(page);
  const historyListContainer = document.getElementById("gameHistory");
  historyListContainer.innerHTML = historyList.results
    .map((match) => {
      const date = new Date(match.date).toLocaleDateString("fr-FR", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
      return `
      <li class="list-group-item">
        <div class="d-flex justify-content-between">
          <span><strong>${match.user1}</strong> vs <strong>${match.user2}</strong></span>
          <span>${match.winner === match.user1 ? `<strong>${match.user1}</strong> a gagné` : `<strong>${match.user2}</strong> a gagné`}</span>
        </div>
        <small class="text-muted">Date: ${date}</small>
      </li>
    `;
    })
    .join("");
  addPrevNextButtons(historyList, historyListContainer, injectHistoryList);
}

function addPrevNextButtons(dataList, ListContainer, injectListFunction) {
  const createButton = (text, onClickFunction, disabled) => {
    const button = document.createElement("button");
    button.textContent = text;
    button.className = "btn btn-primary button-spacing";
    button.onclick = onClickFunction;
    button.disabled = disabled;
    return button;
  };

  const prevButton = createButton("Précédent", () => {
    if (dataList.prevPage) {
      currentHistoryPage--;
      injectListFunction(currentHistoryPage);
    }
  }, !dataList.prevPage);

  const nextButton = createButton("Suivant", () => {
    if (dataList.nextPage) {
      currentHistoryPage++;
      injectListFunction(currentHistoryPage);
    }
  }, !dataList.nextPage);

  ListContainer.appendChild(prevButton);
  ListContainer.appendChild(nextButton);
}


export function injectUserInfo(profile) {
  const avatarElement = document.getElementById("avatar");
  const usernameElement = document.getElementById("username");
  const emailElement = document.getElementById("email");
  const twofaElement = document.getElementById("2fa");

  avatarElement.src = profile.avatar || "../images/profile.jpg";
  usernameElement.value = profile.username;
  emailElement.value = profile.email;
  twofaElement.textContent = `2FA: ${profile.is2FA ? "Yes" : "No"}`;
}

export function prepareUpdateData(profile, fields) {
  let dataToUpdate = {};
  fields.forEach((field) => {
    const newValue = document.getElementById(field).value;
    if (newValue !== profile[field]) {
      const key = field === "email" ? "new_email" : field;
      dataToUpdate[key] = newValue;
    }
  });
  return dataToUpdate;
}

export function printConfirmationMessage(
  texte = "Veuillez vérifier votre nouvelle adresse email pour confirmer le changement.",
  fieldId = "submit_button"
) {
  const messageElement = document.createElement("span");
  messageElement.id = "ConfirmationMessage" + fieldId;
  messageElement.innerText = texte;
  messageElement.style.color = "green";
  messageElement.style.marginLeft = "10px";
  const emailInput = document.getElementById(fieldId);
  emailInput.parentNode.insertBefore(messageElement, emailInput.nextSibling);

  setTimeout(() => {
    messageElement.remove();
  }, 9000);
}

// function formatGameHistory(history, profile) {
//   return history
//     .map((game) => {
//       const date = new Date(game.date).toLocaleString();
//       const opponent =
//         game.user1 === profile.username ? game.user2 : game.user1;
//       const result = game.winner === profile.username ? "Won" : "Lost";
//       return `<li>${date}: ${opponent} - ${result}</li>`;
//     })
//     .join("");
// }
