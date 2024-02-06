import { api_url } from "../main.js";
import {
  getDataWithToken,
  fetchTemplate,
  loadProfileCss,
  requestDataWithToken,
} from "../pageUtils.js";

async function getProfile() {
  const urlProfile = api_url + "users/profile/me";
  const response = await getDataWithToken(urlProfile);
  if (!response.ok) {
    throw new Error("Failed to get profile");
  }
  const data = await response.json();
  return data;
}

// async function getGameHistory() {
//   const urlHistory = api_url + "history/me";
//   const response = await getDataWithToken(urlHistory);
//   if (!response.ok) {
//     throw new Error("Failed to get game history");
//   }
//   const history = await response.json();
//   return history;
// }

async function getFriendList() {
  const url = api_url + "users/friends";
  const response = await getDataWithToken(url);
  if (!response.ok) {
    throw new Error("Failed to get friend list");
  }
  const data = await response.json();
  return data;
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

function injectFriendList(friendList) {
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

function injectUserInfo(profile) {
  const avatarElement = document.getElementById("avatar");
  const usernameElement = document.getElementById("username");
  const emailElement = document.getElementById("email");
  const twofaElement = document.getElementById("2fa");

  avatarElement.src = profile.avatar || "../images/profile.jpg";
  usernameElement.value = profile.username;
  emailElement.value = profile.email;
  twofaElement.textContent = `2FA: ${profile.is2FA ? "Yes" : "No"}`;
}

export async function displayProfile() {
  loadProfileCss("public/css/profile.css");
  try {
    const profileHtml = await fetchTemplate("public/html/profile.html");
    document.getElementById("main").innerHTML = profileHtml;
    const profile = await getProfile();
    const friendList = await getFriendList();
    injectFriendList(friendList);
    injectUserInfo(profile);
    handleSubmit(profile);
  } catch (error) {
    console.error("Error:", error);
  }
}

async function handleSubmit(profile) {
  document
    .getElementById("submit_button")
    .addEventListener("click", async function () {
      const newValue = document.getElementById("username").value;

      try {
        const response = await requestDataWithToken(
          api_url + "users/profile/update",
          { username: newValue },
          "PATCH"
        );

        if (response.status === 200) {
          console.log("Modification réussie !");
          document.getElementById("username").value = newValue;
        } else {
          console.error("Erreur lors de la modification");
          document.getElementById("username").value = profile.username;
        }
      } catch (error) {
        console.error("Error :", error);
      }
    });
}
