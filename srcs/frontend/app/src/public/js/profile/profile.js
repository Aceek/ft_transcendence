import { api_url } from "../main.js";
import { getDataWithToken } from "../pageUtils.js";

async function getProfile() {
  const urlProfile = api_url + "users/profile/me";
  const response = await getDataWithToken(urlProfile);
  if (!response.ok) {
    throw new Error("Failed to get profile");
  }
  const data = await response.json();
  return data;
}

async function getGameHistory() {
  const urlHistory = api_url + "history/me";
  const response = await getDataWithToken(urlHistory);
  if (!response.ok) {
    throw new Error("Failed to get game history");
  }
  const history = await response.json();
  return history;
}

function formatGameHistory(history, profile) {
  return history
    .map((game) => {
      const date = new Date(game.date).toLocaleString();
      const opponent =
        game.user1 === profile.username ? game.user2 : game.user1;
      const result = game.winner === profile.username ? "Won" : "Lost";
      return `<li>${date}: ${opponent} - ${result}</li>`;
    })
    .join("");
}

function loadProfileCss() {
  const head = document.head;
  const link = document.createElement("link");

  link.type = "text/css";
  link.rel = "stylesheet";
  link.href = "public/css/profile.css";

  head.appendChild(link);
}

// export async function displayProfile() {
//   try {
//     loadProfileCss();
//     const profile = await getProfile();
//     const history = await getGameHistory();

//     const response = await fetch("public/html/profile.html");
//     const profileBlock = await response.text();

//     document.getElementById("main").innerHTML = profileBlock;

//     document.getElementById("avatar").src = profile.avatar;
//     document.getElementById("username").textContent = profile.username;
//     document.getElementById("email").textContent = profile.email;
//     document.getElementById("2fa").textContent = profile.is_2fa_enabled
//       ? "2FA is enabled"
//       : "2FA is not enabled";
//     document.getElementById("friends").innerHTML = profile.friends
//       .map((friend) => `<li>${friend}</li>`)
//       .join("");
//     document.getElementById("history").innerHTML = formatGameHistory(
//       history,
//       profile
//     );
//   } catch (error) {
//     console.error("Error:", error);
//   }
// }



// realy simple function that display html profile page
export async function displayProfile() {
  loadProfileCss();
  try {
    fetch("public/html/profile.html")
      .then((response) => response.text())
      .then((data) => {
        document.getElementById("main").innerHTML = data;
      });
  } catch (error) {
    console.error("Error:", error);
  }
}
