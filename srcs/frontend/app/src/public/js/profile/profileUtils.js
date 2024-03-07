import { router } from "../main.js";
import { requestDataWithToken } from "../pageUtils.js";
import { getGameHistory, getFriendList } from "./getProfile.js";
import { createButtonFriend } from "./profileFriends.js";
import { sendTrackStatus } from "../user_activity_websocket/user_activity_utils.js";
import { api_url } from "../main.js";

const historyContext = {
  currentPage: 1,
  updatePage: function (page, UID = null) {
    this.currentPage = page;
    injectHistoryList(this.currentPage, UID);
  },
};

export const friendContext = {
  currentPage: 1,
  updatePage: function (page, UID = null) {
    this.currentPage = page;
    injectFriendList(this.currentPage, UID);
  },
};

export async function sendUpdateRequest(url, data, method = "PATCH") {
  try {
    const response = await requestDataWithToken(url, data, method);
    if (response.status === 200) {
      return true;
    } else {
      console.error(response.statusText);
      return false;
    }
  } catch (error) {
    console.error("Error :", error);
    return false;
  }
}

export function onclickFunctionDeleteContainer(container) {
  container.remove();
}

export async function attachLinkListenerProfile() {
  const profileLinks = document.querySelectorAll(".profile-link");
  profileLinks.forEach((link) => {
    if (!link.getAttribute("data-listener-added")) {
      link.addEventListener("click", () => {
        const uid = link.getAttribute("data-uid");
        router("/profile/" + uid);
      });
      link.setAttribute("data-listener-added", "true");
    }
  });
}

export async function injectFriendList(page, UID = null) {
  const friendList = await getFriendList(page, UID);
  const friendListContainer = document.getElementById("friendsList");
  sendTrackStatus(friendList.results.map((friend) => friend.id));

  friendListContainer.innerHTML = "";
  const friendListTitle = document.getElementById("friendListTitle");
  friendListTitle.textContent = "Friend List";

  await Promise.all(
    friendList.results.map(async (friend) => {
      const listItem = document.createElement("li");
      listItem.className =
        "list-group-item d-flex align-items-center justify-content-between";

      listItem.innerHTML = `
      <div class="friend-info d-flex align-items-center">
        <img src="${friend.avatar || "/public/images/profile.jpg"}" alt="Avatar de ${friend.username}" class="rounded-circle me-3" width="75" height="75">
        <div>
          <span class="profile-link" data-uid="${friend.id}"><strong>${friend.username}</strong></span>
          <span id="status-${friend.id}" class=${friend.status === "online" ? "text-success" : "text-danger"}>• ${friend.status}</span>
        </div>
      </div>
    `;

      const removeButton = await createButtonFriend(
        friend.id,
        "users/remove_friends",
        () => {
          onclickFunctionDeleteContainer(listItem);
        }
      );
      removeButton.textContent = "Remove";
      removeButton.classList.add("btn-danger");
      listItem.appendChild(removeButton);
      friendListContainer.appendChild(listItem);
    })
  );

  await attachLinkListenerProfile();
  addPrevNextButtons(friendList, friendListContainer, friendContext);
}

export async function injectHistoryList(page, UID = null) {
  const historyList = await getGameHistory(page, UID);
  const historyListContainer = document.getElementById("gameHistory");
  if (!historyListContainer) {
    return;
  }
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
  addPrevNextButtons(historyList, historyListContainer, historyContext, UID);
}

export function addPrevNextButtons(dataList, container, context, UID = null) {
  const createButton = (text, onClickFunction) => {
    const button = document.createElement("button");
    button.classList.add("button-container");
    button.textContent = text;
    button.className = "btn btn-primary button-spacing";
    button.onclick = onClickFunction;
    return button;
  };
  if (dataList.prevPage) {
    const prevButton = createButton("Précédent", () => {
      context.updatePage(context.currentPage - 1, UID);
    });
    container.appendChild(prevButton);
  }

  if (dataList.nextPage) {
    const nextButton = createButton("Suivant", () => {
      context.updatePage(context.currentPage + 1, UID);
    });
    container.appendChild(nextButton);
  }
}

export function injectUserInfo(profile) {
  const avatarElement = document.getElementById("avatar");
  const usernameElement = document.getElementById("username");
  const emailElement = document.getElementById("email");

  avatarElement.src = profile.avatar || "/public/images/profile.jpg";
  usernameElement.value = profile.username;
  emailElement.value = profile.email;
  injectTwofaButton(profile);
}

export function attashTwofaButtonListener(twofaButton, profile) {
  twofaButton.addEventListener("click", async (e) => {
    e.preventDefault();
    const dataToUpdate = {};
    dataToUpdate["is_2fa_enabled"] = !profile.is_2fa_enabled;
    const updateSuccess = await sendUpdateRequest(
      api_url + "users/profile/update",
      dataToUpdate
    );

    if (updateSuccess) {
      console.log("2FA modifié avec succès !");
      if (profile.is_2fa_enabled) {
        profile.is_2fa_enabled = false;
      } else {
        profile.is_2fa_enabled = true;
      }
      injectUserInfo(profile);
    } else {
      console.error("Erreur lors de la modification de 2FA.");
    }
  });

  document.getElementById("profileDivButton").appendChild(twofaButton);

  // document.getElementById("profileDivButton").insertBefore(twofaButton, document.getElementById("profileDivButton").firstChild);

}

export function injectTwofaButton(profile) {
  let twofaButton = document.getElementById("twofaButton");
  if (twofaButton) {
    twofaButton.remove();
  }
  twofaButton = document.createElement("button");
  twofaButton.id = "twofaButton";
  twofaButton.classList.add("btn", "btn-primary");

  if (profile.is_2fa_enabled) {
    twofaButton.textContent = "2FA:OFF";
  } else {
    twofaButton.textContent = "2FA:ON";
  }

  twofaButton.classList.add("btn", "btn-primary");

  attashTwofaButtonListener(twofaButton, profile);
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
  fieldId = "emailDiv",
  color = "green"
) {
  if (document.getElementById("ConfirmationMessage" + fieldId)) {
    return;
  }

  const messageElement = document.createElement("div");
  messageElement.id = "ConfirmationMessage" + fieldId;
  messageElement.innerText = texte;
  messageElement.style.color = color;
  messageElement.style.marginLeft = "10px";
  const containerToAppend = document.getElementById(fieldId);
  containerToAppend.insertAdjacentElement("afterend", messageElement);

  setTimeout(() => {
    messageElement.remove();
  }, 2000);
}
