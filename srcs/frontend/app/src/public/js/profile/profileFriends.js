import { api_url, router } from "../main.js";
import { getProfile, getFriendList } from "./getProfile.js";
import { injectUserInfo, injectHistoryList } from "./profileUtils.js";
import { loadProfileCss, fetchTemplate } from "../pageUtils.js";
import { sendUpdateRequest } from "./profileUtils.js";

export async function displayFriendsProfile(UID) {
  loadProfileCss("/public/css/profile.css");
  try {
    const profileHtml = await fetchTemplate("/public/html/profile.html");
    document.getElementById("main").innerHTML = profileHtml;
    const profile = await getProfile(UID);
    injectUserInfo(profile);
    await injectHistoryList(1, UID);
    await eventListenerButtonStats(UID);
    ajusterInterfaceProfil();
    await addFriendsButton(profile.id);
  } catch (error) {
    console.error("Error:", error);
    router("/home"); // redirect to 404 page
  }
}

async function eventListenerButtonStats(userUID = null) {
  const statsButton = document.getElementById("statsButton");
  statsButton.addEventListener("click", async () => {
    await router("/profile/" + userUID + "/stats");
  });
  statsButton.disabled = false;
}

export async function createButtonFriend(
  userUID,
  url = "users/profile/update",
  onButtonClick = null
) {
  const friendButton = document.createElement("button");
  friendButton.id = "addFriendButton";
  friendButton.classList.add("button-container");
  friendButton.className = "btn btn-primary button-spacing";
  friendButton.textContent = "Add";
  friendButton.onclick = async function () {
    try {
      let dataToUpdate = {};
      dataToUpdate["friends"] = [userUID];
      const updateSuccess = await sendUpdateRequest(
        api_url + url,
        dataToUpdate
      );
      if (updateSuccess) {
        console.log("Ami ajouté / supprimé avec succès");
        if (onButtonClick) onButtonClick();
        friendButton.remove();
      } else {
        console.error("Erreur lors de l'ajout / suppresion de l'ami");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };
  return friendButton;
}

async function addFriendsButton(userUID) {
  try {
    const profileConnected = await getProfile();
    const profileConnectedUID = profileConnected.id;
    if (profileConnectedUID === userUID) {
      return;
    }
    const friendsList = await getFriendList(0);
    const profileDiv = document.getElementById("profileDiv");
    if (friendsList.results.some((friends) => friends.id === userUID)) {
      const friendButton = await createButtonFriend(
        userUID,
        "users/remove_friends",
        () => {
          addFriendsButton(userUID);
        }
      );
      friendButton.textContent = "Remove";
      friendButton.classList.add("btn-danger");
      profileDiv.appendChild(friendButton);
      return;
    } else {
      const friendButton = await createButtonFriend(
        userUID,
        "users/profile/update",
        () => {
          addFriendsButton(userUID);
        }
      );
      profileDiv.appendChild(friendButton);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

export function ajusterInterfaceProfil() {
  const username = document.getElementById("username");
  username.disabled = true;
  const emailDiv = document.getElementById("emailDiv");
  emailDiv.remove();
  const avatarUpload = document.getElementById("avatarUpload");
  avatarUpload.remove();
  const avatar = document.getElementById("avatar");
  avatar.style.marginBottom = "10px";
  const friendsListCol = document.getElementById("friends-list-col");
  friendsListCol.remove();
  const editAccountButton = document.getElementById("editAccountButton");
  editAccountButton.remove();
  const twofaElement = document.getElementById("2fa");
  twofaElement.remove();
  const gameHistoryDiv = document.getElementById("gameHistoryDiv");
  gameHistoryDiv.className = "col-md12 col-lg-12";
  const profileButton = document.getElementById("profileButton");
  profileButton.disabled = true;
}
